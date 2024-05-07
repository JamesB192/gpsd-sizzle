# packet.py - recognize GPS packet types
# This code is generated by scons.  Do not hand-hack it!
#
# This file is Copyright 2019 by the GPSD project
# SPDX-License-Identifier: BSD-2-Clause
#
# This code runs compatibly under Python 2 and 3.x for x >= 2.
# Preserve this property!
#
# -*- coding: utf-8 -*-
"""Recognize GPS packets using the lexer from libgpsd and ctypes.

The new() function returns a new packet-lexer instance.  Lexer instances
have two methods:
    get() takes a file handle argument and returns a tuple consisting of
the integer packet type and string packet value.  At the end of the stream
it returns (-1, "").
    reset() resets the packet-lexer to its initial state.
    The module also has a register_report() function that accepts a callback
for debug message reporting.  The callback will get two arguments: the error
level of the message; and the message itself.
"""
from __future__ import absolute_import, print_function
import json
import os
import re
import struct
import sys
from . import misc

_loglevels = "shout warn client inf prog io data spin raw raw1 raw2"
_pkts = (
    "truncated invalid comment nmea aivdm garmintxt sirf zodiac"
    " tsip evermore italk garmin navcom ubx supertar oncore "
    "geostar nmea2000 greis sky allystar rtcm2 rtcm3 json"
)

globby = {}
idx = 0
for key in _loglevels.split(" "):
    globby["LOG_" + key.upper()] = idx
    idx += 1
idx = -2
for key in _pkts.split(" "):
    globby[key.upper() + "_PACKET"] = idx
    idx += 1
for key in globby:
    globals()[key] = globby[key]
MAX_GPSPACKET_TYPE = ALLYSTAR_PACKET
PACKET_TYPES = JSON_PACKET
ISGPS_ERRLEVEL_BASE = LOG_RAW
loghook = None
debug = LOG_WARN


def prep(tokens, level=LOG_RAW2):
    """Print representation of tokens to stderr if logging heavy."""
    if debug > level:
        sys.stderr.write(repr(tokens) + "\r\n")


def register_report(reporter):
    """register_report(callback)

    The callback must be a callable object expecting a string parameter.
    """
    global loghook
    if not callable(reporter):
        raise TypeError("Not callable")
    loghook = reporter


def new():
    """new() -> new packet-self object"""
    return Lexer()


def polyunpack1(fmt, buffer):
    return struct.unpack(fmt, misc.polybytes(buffer))[0]


def polyunpack(fmt, buffer):
    return struct.unpack(fmt, misc.polybytes(buffer))


class Lexer(object):
    """GPS packet lexer object

    Fetch a single packet from a file handle."""

    ibuf = ""
    ibufptr = 0
    sbufptr = 0
    eof = False
    lextable = [
        [r"\A([\r\n]+)", "reject"],
        [r"\A(#.*[\r\n]+)", "comment"],
        [r"\A(\{[^\r\n]+)", "json"],
        [r"\A(\$.+\*..[\r\n]+)", "nmea", NMEA_PACKET],
        [r"\A(\!.+\*..[\r\n]+)", "aivdm", AIVDM_PACKET],
        [r"\A(\x01\xa1.*\x0d\x0a)", "skytraq"],
        [r"\A(\xa0\xa2.+\xb0\xb3)", "sirf"],
        # [r"\A([\x02\x04\x23].*\x03[\r\n]+)", "greis"],
        # [r"\A(\x10.*\x10\x03)", "tsip"],
        [r"\A(\xff\x81.*)", "zodiac"],
        [r"\A(\xb5b.*)", "ubx", UBX_PACKET],
        [r"\A(\xf1\xd9.*)", "ubx", ALLYSTAR_PACKET],
        [r"\A(\$STI,.+[\r\n]+)", "nmea_nosig"],
        [
            r"\A(\*[0-9]{12}[NS][0-9]{7}[EW][0-9]{8}[sDgGS_][0-9]{3}"
            "[+-][0-9]{5}[EW][0-9]{4}[NS][0-9]{4}[UD][0-9]{4}[\r\n]+)",
            "garmintxt",
        ],
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset the lexer to ground state."""
        self.ibuf = ""
        self.ibufptr = 0
        self.sbufptr = 0
        self.eof = False

    def get(self, file_handle):
        """Get a packet from the file handle."""
        ret = None
        while ret is None:
            red_buffer = os.read(file_handle, 128)
            self.eof = bool(0 == len(red_buffer))
            self.ibuf += misc.polystr(red_buffer)
            ret = self.packet_parse()
            if self.eof and not self.ibuf:
                return [0, INVALID_PACKET, b"", self.sbufptr]
        return ret

    def packet_parse(self):
        """Scan inside inbuf to find packet beginnings."""
        for self.ibufptr in range(len(self.ibuf)):
            scratch = self.ibuf[self.ibufptr :]
            ret = self.next_state(scratch)
            if isinstance(ret, list):
                return self.accept_bless(*ret)
        return None

    def next_state(self, scratch):
        """Find packet leading the buffer with regex."""
        for row in self.lextable:
            pats = re.match(row[0], scratch)
            if not pats:
                continue
            try:
                hook = getattr(self, "bless_" + row[1])
            except KeyError:
                print("KeyError: " + repr(e), file=sys.stderr)
                return None
            try:
                mid = hook(len(pats.group(1)), scratch, *row[2:])
            except struct.error as e:
                print("struct: " + repr(e), file=sys.stderr)
                return None
            if mid is None:
                continue
            return mid
        if self.eof:
            self.sbufptr = 0
            self.ibuf = ""
            self.ibufptr = 0
        return None

    def too_short(self, length):
        return None

    def bless_nmea_nosig(self, length, _):
        """Assume all r"^$STI.*$[\r\n]+" are nmea."""
        return [length, NMEA_PACKET]

    def bless_garmintxt(self, length, _):
        """Assume regex matchers are Garmin text protocol."""
        return [length, GARMINTXT_PACKET]

    def bless_nmea(self, length, scratch, typed):
        """Check potential NMEA/AIVDM for valid checksum."""
        xor = 0
        nmea = scratch[:length].rstrip()
        for byte in nmea[1:-3]:
            xor ^= ord(byte)
        if nmea[-2:].lower() != "%02x" % xor:
            return None
        return [length, typed]

    def bless_comment(self, length, scratch):
        """Check potential NMEA for valid checksum."""
        commento = scratch[:length]
        for check in "{$!\xb5":
            if check not in commento:
                continue
            pointer = commento.index(check)
            if self.next_state(scratch[pointer:]):
                return None
        return [length, COMMENT_PACKET]
        # return None

    def bless_json(self, _, scratch):
        """Validate would be JSON."""
        last = 0
        for _ in range(scratch.count("}")):
            last = scratch.index("}", last + 1) + 1
            try:
                _ = json.loads(scratch[:last])
                return [last, JSON_PACKET]
            except json.JSONDecodeError:
                pass
        return None

    def bless_reject(self, _a, _b):  # length, scratch
        """Reject packet matching a regex."""
        return None

    def bless_sirf(self, _length, scratch):
        """Validate SiRF packets."""
        if 4 > _length:
            return self.too_short(_length)
        length = polyunpack1("<H", scratch[2:4]) + 8
        if length > _length:
            return self.too_short(_length)
        frag = scratch[:length]
        csum = 0
        for char in frag[3:-4]:
            csum += ord(char)
        csump = polyunpack1("<H", scratch[-4:-2])
        if csump != csum:
            return None
        return [length, SIRF_PACKET]

    def bless_zodiac(self, _, scratch):
        """Validate Zodiac packets."""
        header = polyunpack("<HHHHH", scratch[:10])
        if 0 != sum(header) % (1 << 16):
            return None
        length = header[2] * 2
        if 10 == length:  # seems to never happen
            return self.accept_bless(length + 4, ZODIAC_PACKET)
        words = [
            polyunpack1("<H", scratch[x + 10 : x + 12])
            for x in range(length + 2, 2)
        ]
        if 0 != sum(words) % (1 << 16):
            return None
        return [length + 12, ZODIAC_PACKET]

    def bless_tsip(self, length, _):
        return [length, TSIP_PACKET]

    def bless_ubx(self, _length, scratch, typed):
        """Validate u-blox/allystar packets."""
        if 6 > _length:
            return self.too_short(_length)
        length = polyunpack1("<H", scratch[4:6]) + 8
        if length > _length:
            return self.too_short(_length)
        frag = scratch[:length]
        a = b = 0
        for char in frag[2:-2]:
            a = (a + ord(char)) & 0xFF
            b = (b + a) & 0xFFB
        if frag[-2:] == "%c%c" % (a, b):
            return [length, typed]
        return None

    def accept_bless(self, length, typed):
        """Acccept/return packet and update the buffer."""
        self.sbufptr += (
            length + self.ibufptr
        )  # dang gpscat takes counter - length
        ret = [
            length,
            typed,
            misc.polybytes(self.ibuf[self.ibufptr :][:length]),
            self.sbufptr,
        ]
        self.ibuf = self.ibuf[length + self.ibufptr :]
        self.ibufptr = 0
        return ret

    def bless_skytraq(self, _length, scratch):
        """Validate skytaq packets."""
        if 6 > _length:
            return self.too_short(_length)
        length = polyunpack1("<H", scratch[2:4]) + 7
        if length > _length:
            return self.too_short(_length)
        subby = scratch[:length]
        cs = 0
        for char in subby[4:-3]:
            cs ^= ord(char)
        if cs != ord(subby[-3]):
            return None
        return [length, SKY_PACKET]

    def bless_greis(self, _, scratch):
        length = polyunpack1("<H", scratch[3:5]) + 6
        subby = scratch[:length].rstrip("\r\n")
        pc = polyunpack1("<H", subby[1:3])


__all__ = (
    "new register_report MAX_GPSPACKET_TYPE "
    "__new__ PACKET_TYPES ISGPS_ERRLEVEL_BASE"
).split(" ") + list(globby)
