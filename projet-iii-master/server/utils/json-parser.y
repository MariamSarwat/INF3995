/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */


%{

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/io.h"
#include "utils/buf.h"
#include "utils/json.h"

#include "./json-parser.h"

	int json_parse(FILE *fp, struct json **obj);

	static int json_lex(JSON_STYPE *val_p, JSON_LTYPE *loc_p, FILE *fp);
	static void json_error(JSON_LTYPE  *loc_p, FILE *fp, struct json **obj, const char *err);


#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wswitch-enum"
%}

%union {
	int          tri_state;
	double       number;
	char        *string;
	struct json *obj;
}

%define api.prefix {json_}
%debug
%locations
%define api.pure full
%define parse.error verbose

%parse-param {FILE *fp}
%parse-param {struct json **obj}
%lex-param   {FILE* fp}

%token <tri_state>  TRI;
%token <number>     NUM;
%token <string>     STR;

%type <obj> value
%type <obj> value_sequence
%type <obj> entry_sequence
%type <obj> dict
%type <obj> array

%destructor { free($$); } STR;
%destructor { json_destroy($$); } <obj>;

%%
START:
/*  Empty  */
|
START value
{
	*obj = $2;
	YYACCEPT;
}
;

entry_sequence:
STR ':' value
{
	$$ = json_dict();
	json_dict_set($$, $1, $3);
	free($1);
}
|
entry_sequence ',' STR ':' value
{
	$$ = $1;
	json_dict_set($1, $3, $5);
	free($3);
}
;


dict:
'{' entry_sequence '}'
{
	$$ = $2;
}
|
'{' '}'
{
	$$ = json_dict();
}
;

array:
'[' value_sequence ']'
{
	$$ = $2;
}
|
'[' ']'
{
	$$ = json_array();
}
;

value_sequence:
value
{
	$$ = json_array();

	json_array_push($$, $1);
}
|
value_sequence ',' value
{
	json_array_push($1, $3);

	$$ = $1;
}
;

value:
STR
{
	$$ = json_string($1);
	free($1);
}
| NUM
{
	$$ = json_number($1);
}
| dict
{
	$$ = $1;
}
| array
{
	$$ = $1;
}
| TRI
{
    if ($1 == -1) {
	$$ = json_null();
    } else {
	$$ = json_boolean((bool)$1);
    }
}
;
%%

void json_error(JSON_LTYPE *loc_p, FILE *fp,
                struct json **obj, const char *err)
{
	(void)obj;

	if (feof(fp)) {
		return;
	}

	error("%s at %d.%d-%d.%d\n",
	      err,
	      loc_p->first_line,
	      loc_p->last_line,
	      loc_p->first_column,
	      loc_p->last_column);
}


#define SKIP_WS(c, fd) while((c = fgetc(fd)) == ' ' || c == '\t')

/**
 * @brief Read a word from a stream.
 *
 * @param [out] buf The buffer to fill.
 *
 * @param [in] fd The stream to read from
 *
 * @return The number of characters readed from stream.
 */
static usize get_word(char **pbuf, FILE *fp)
{
	char c;
	char *buf;

	buf_new(buf);

	while (isalnum(c = fgetc(fp))) {
		buf_push(buf, &c);

	}

	ungetc(c, fp);

	c = '\0';
	buf_push(buf, &c);

	*pbuf = buf;

	return buf_cnt(buf) - 1;
}


/**
 * @brief JSON Lexer.
 *
 * @param [out] val_p Pointer to the value used by json_parser
 *
 * @param [out] loc_p Pointer to the location used by json_Parser
 *
 * @param [in] fd File descriptor to read from
 *
 * @return Token type.
 */
int json_lex(JSON_STYPE *val_p, JSON_LTYPE *loc_p, FILE *fp)
{
	int c;

	SKIP_WS(c, fp) {
		++(loc_p->last_column);
	}

	loc_p->first_line   = loc_p->last_line;
	loc_p->first_column = loc_p->last_column;

	if (c == EOF) {
		return 0;
	}

	if (c == '\n') {
		loc_p->last_line++;
		loc_p->last_column = 0;

		SKIP_WS(c, fp) {
			loc_p->last_column++;
		}
	}

	if (c == '"') {
		char  *buf = NULL;
		usize len  = 0;
		isize size = getdelim(&buf, &len, '"', fp);

		buf[size - 1] = '\0';

		val_p->string = strdup(buf);
		loc_p->last_column += size;

		free(buf);

		return STR;
	}

	if (isdigit(c) || c == '-') {
		double x;
		int n;

		ungetc(c, fp);
		loc_p->last_column--;

		fscanf(fp, "%lf%n", &x, &n);

		val_p->number = x;

		loc_p->last_column += n;

		return NUM;
	}

	if (isalpha(c)) {

		char *buf;
		usize n;

		ungetc(c, fp);

		--loc_p->last_column;

		n = get_word(&buf, fp);

		if (n) {
			if (streq(buf, "true")) {
				val_p->tri_state = 1;
				loc_p->last_column += n;
				buf_del(buf);
				return TRI;
			}
			else if (streq(buf, "false")) {
				val_p->tri_state = 0;
				loc_p->last_column += n;
				buf_del(buf);
				return TRI;
			}
			else if (streq(buf, "null")) {
				val_p->tri_state = -1;
				loc_p->last_column += n;
				buf_del(buf);
				return TRI;
			}

			for (int i=n-1; i >= 0; --i) {
				ungetc(buf[i], fp);
			}

			buf_del(buf);
		}
	}

	return c;
}
