#ifndef UTILS_JSON
#define UTILS_JSON

#include <stdio.h>

struct json;

extern int json_parse(FILE *fp, struct json **obj);

extern struct json *json_null(void);
extern struct json *json_boolean(bool boolean);
extern struct json *json_number(double number);
extern struct json *json_string(const char *string);
extern struct json *json_string_acquire(char *string);
extern struct json *json_array(void);
extern struct json *json_dict(void);

extern bool json_is_null(const struct json *value) __pure;
extern bool json_is_boolean(const struct json *value) __pure;
extern bool json_is_number(const struct json *value) __pure;
extern bool json_is_string(const struct json *value) __pure;
extern bool json_is_array(const struct json *value) __pure;
extern bool json_is_dict(const struct json *value) __pure;

extern bool json_to_boolean(const struct json *value) __pure;
extern double json_to_number(const struct json *value) __pure;
extern const char *json_to_string(const struct json *value) __pure;

extern int json_array_push(struct json *array, struct json *value);
extern int json_dict_set(struct json *dict, const char *label, struct json *value);
extern struct json *json_dict_get(const struct json *dict, const char *label) __pure;
extern struct json *json_search(const struct json *dict, ... /* NULL */) __pure;

extern void json_destroy(struct json *value);

extern isize json_streamfd(const struct json *value, int fd);
extern isize json_stream(const struct json *value, FILE *fp);
extern void  json_stream_http(const struct json *value, FILE *fp);
extern char *json_dostringify(const struct json *value, bool escape);
#define json_stringify(VALUE) json_dostringify(VALUE, true)
#define json_stringify2(VALUE) json_dostringify(VALUE, false)

#endif
