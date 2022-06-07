#ifndef HTTP_H
#define HTTP_H

#include <stdio.h>

enum http_status {
#define X(NAME, STATUS) CAT(HTTP_, NAME) = STATUS,
#include "utils/http.xlist"
#undef X
};

enum http_method {
	HTTP_GET,
	HTTP_PUT,
	HTTP_POST,
	HTTP_PATCH,
	HTTP_DELETE,
	HTTP_METHOD_MAX
};

struct http_request {
	char *URI;
	char **fields;
	char *authorization;
	usize content_length;
	enum http_method method;
};

extern const char *http_method_names[];

extern int http_get_method(const char *method_name) __notnull __pure;

__notnull
extern int http_scan(struct http_request *request, FILE *fp) __notnull;

extern void http_clean(struct http_request *request);

extern void http_add_field(struct http_request *request, const char *field) __notnull;
extern void http_del_fields(struct http_request *request) __notnull;
extern const char *http_field_value(const struct http_request *request, const char *name) __notnull __pure;

extern void http_set_URI(struct http_request *request, const char *URI) __notnull;
extern void http_del_URI(struct http_request *request) __notnull;

extern const char *http_status_string(enum http_status status) __const;

extern enum http_status http_auth(const struct http_request *request, char **puser) __notnull;
extern bool http_auth_set(const char *user, const char *passwd) __notnull __const;

#endif
