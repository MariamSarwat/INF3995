/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 *
 * utils/http-parser.l - HTTP scanner using flex
 *
 * See flex(1) and the Texinfo of flex.
 */

%{
#include <limits.h>

#include "core/io.h"
#include "utils/http.h"

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsuggest-attribute=pure"
#pragma GCC diagnostic ignored "-Wsuggest-attribute=malloc"
#pragma GCC diagnostic ignored "-Wnull-dereference"
#pragma GCC diagnostic ignored "-Wstrict-overflow"
%}

 /* Definitions */
%option 8bit
%option warn
%option always-interactive
%option pointer
%option reentrant
%option noyywrap
%option noyylineno
%option nounput
%option nodefault
%option noinput
%option debug
%option prefix="http_yy"
%option extra-type="struct http_request *"

%x REQUEST_URI
%X REQUEST_VERSION
%x FIELD_SEQUENCE
%x BODY

CRLF			"\r\n"
HTTP_METHOD		GET|PUT|POST
HTTP_VERSION            "HTTP/1.1"
URI			"/"[^# ]*
FIELD_NAME		([a-zA-Z0-9]|[-_ ])+
FIELD_VALUE		[^\r\n]+

 /* Rules */
%%

 /* Request line */
<INITIAL>^{HTTP_METHOD}[ ] {
	BEGIN(REQUEST_URI);
	yytext[yyleng - 1] = '\0';
	yyextra->method = http_get_method(yytext);
	yytext[yyleng - 1] = ' ';
}

<REQUEST_URI>{URI} {
	BEGIN(REQUEST_VERSION);
	http_set_URI(yyextra, yytext);
}

<REQUEST_VERSION>{HTTP_VERSION}{CRLF} {
	BEGIN(FIELD_SEQUENCE);
        debug("%s %s",
              http_method_names[yyextra->method],
              yyextra->URI);
}

 /* Field sequence
  *
  * We don't support multi-line field value.
  */
<FIELD_SEQUENCE>{

(?i:content-length)":"[^\r\n]+{CRLF} {

        usize len;

        len = strtoul(yytext+16, NULL, 10);

        if (ULONG_MAX == len && errno == ERANGE) {
                return -1;
        }

        yyextra->content_length = len;

        debug("Content-Length: %zu", len);
}

(?i:authorization)":"[^\r\n]+{CRLF} {

        yytext[yyleng - 2] = '\0';
        yyextra->authorization = strdup(yytext + 14);

        debug("Authorization: %s", yyextra->authorization);
}

{FIELD_NAME}":"{FIELD_VALUE}{CRLF} {
	yytext[yyleng - 2] = '\0';
	http_add_field(yyextra, yytext);
        debug(yytext);
}

{CRLF} {
	BEGIN(INITIAL); return 1;
}

}

 /* Don't care about spaces */
<INITIAL,REQUEST_URI,REQUEST_VERSION>[ \t]+  { }

<INITIAL><<EOF>> { return 0; }
<REQUEST_URI,REQUEST_VERSION,FIELD_SEQUENCE><<EOF>> { return -1; }

 /* Default rule */
<*>.|\n { return -1; }

%%

int http_scan(struct http_request *req, FILE *in)
{
    yyscan_t scanner = NULL;
    int err;

    if (http_yylex_init_extra(req, &scanner)) {
	panic("fail to scan request: %m");
    }

    http_yyset_in(in, scanner);

    err = http_yylex(scanner);

    http_yylex_destroy(scanner);

    return err;
}
