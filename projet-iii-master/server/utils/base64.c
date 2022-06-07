/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include "utils/base64.h"
#include "utils/buf.h"

static const char table[] = {
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
	'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
	'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
	'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
	'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
	'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
	'w', 'x', 'y', 'z', '0', '1', '2', '3',
	'4', '5', '6', '7', '8', '9', '+', '/'
};

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Woverride-init"
static const int rtable[] = {

	[0 ... 255] = -1,

	['A'] = 0,  ['B'] = 1,	['C'] = 2,  ['D'] = 3,	['E'] = 4,  ['F'] = 5,	['G'] = 6,  ['H'] = 7,
	['I'] = 8,  ['J'] = 9,	['K'] = 10, ['L'] = 11, ['M'] = 12, ['N'] = 13, ['O'] = 14, ['P'] = 15,
	['Q'] = 16, ['R'] = 17, ['S'] = 18, ['T'] = 19, ['U'] = 20, ['V'] = 21, ['W'] = 22, ['X'] = 23,
	['Y'] = 24, ['Z'] = 25, ['a'] = 26, ['b'] = 27, ['c'] = 28, ['d'] = 29, ['e'] = 30, ['f'] = 31,
	['g'] = 32, ['h'] = 33, ['i'] = 34, ['j'] = 35, ['k'] = 36, ['l'] = 37, ['m'] = 38, ['n'] = 39,
	['o'] = 40, ['p'] = 41, ['q'] = 42, ['r'] = 43, ['s'] = 44, ['t'] = 45, ['u'] = 46, ['v'] = 47,
	['w'] = 48, ['x'] = 49, ['y'] = 50, ['z'] = 51, ['0'] = 52, ['1'] = 53, ['2'] = 54, ['3'] = 55,
	['4'] = 56, ['5'] = 57, ['6'] = 58, ['7'] = 59, ['8'] = 60, ['9'] = 61, ['+'] = 62, ['/'] = 63,
};
#pragma GCC diagnostic pop


char *base64_encode(const char *data)
{
	u8 c;
	u32 buf;
	uint cnt;
	char *encoded;

	buf_new(encoded);

	cnt = 0;
	buf = 0;

	while ((c = (u8)*data) != '\0') {

		buf = (buf << 8) | c;

		if (3 == ++cnt) {

			char E;

			for (int s=18; s>=0; s-=6) {
				E = table[(buf >> s) & 0b111111];
				buf_push(encoded, &E);
			}

			cnt = 0;
		}

		++data;
	}

	if (2 == cnt) {
		char E;

		E = table[(u8)((buf >> 10) & 0b111111)];
		buf_push(encoded, &E);

		E = table[(u8)((buf >> 4)  & 0b111111)];
		buf_push(encoded, &E);

		E = table[(u8)((buf & 0b1111) << 2)];
		buf_push(encoded, &E);

		E = '=';

		buf_push(encoded, &E);
	} else if (cnt == 1) {

		char E;

		E = table[(u8)((buf >> 2) & 0b111111)];
		buf_push(encoded, &E);

		E = table[(u8)((buf & 0b11) << 4)];
		buf_push(encoded, &E);

		E = '=';

		buf_push(encoded, &E);
		buf_push(encoded, &E);
	}

	c = '\0';

	buf_push(encoded, (char*)&c);

	buf_fit(encoded);

	return encoded;
}

static char *decode(u32 symbols, char *buf)
{
	for (int shift=16; shift>=0; shift -= 8) {
		char c = (symbols >> shift) & 0xFF;
		buf_push(buf, &c);
	}
	return buf;
}

char *base64_decode(const char *data)
{
	char c;
	u32 buf;
	uint cnt;
	char *decoded;

	buf_new(decoded);

	cnt = 0;
	buf = 0;

	while ((c = (u8)*data) != '\0') {

		int index;

		index = rtable[(u8)c];

		/*
		 * Check for padding
		 */
		if (index < 0) {

			if ('=' == c) {

				if ('=' == data[1]) {
					char D = (char)(buf >> 4);
					buf_push(decoded, &D);
				} else {
					char D;
					buf >>= 2;
					D = (char)(buf >> 8);
					buf_push(decoded, &D);
					D = (char)(buf & 0xFF);
					buf_push(decoded, &D);
				}

				break;
			}

			/* Not padding!	 Panic! */
			buf_del(decoded);
			return NULL;
		}

		buf = (buf << 6) | rtable[(u8)c];

		if (4 == ++cnt) {
			decoded = decode(buf, decoded);
			cnt = 0;
		}


		++data;
	}

	c = '\0';

	buf_push(decoded, &c);

	buf_fit(decoded);

	return decoded;
}
