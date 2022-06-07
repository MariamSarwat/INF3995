/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "core/io.h"
#include "utils/hash.h"
#include "utils/json.h"
#include "utils/list.h"

enum json_type {
	JSON_NUMBER = 0b00,
	JSON_STRING = 0b01,
	JSON_ARRAY  = 0b10,
	JSON_DICT   = 0b11,
	JSON_TRI    = 0b100
};

struct json {

	struct list_head node;
	char *label;
	u64 hash;

	union {
		int	       tri_state;
		double	       number;
		char	      *string;
		struct list_head children;
	};

	enum json_type type;
};

static inline enum json_type json_type(const struct json *value)
{
	return value->type;
}

static struct json *json_alloc(void)
{
	struct json *json = calloc(1, sizeof(struct json));

	INIT_LIST_HEAD(&json->node);

	return json;
}

#define json_free(PTR) free(PTR)

bool json_is_null(const struct json *value)
{
	return json_type(value) == JSON_TRI && value->tri_state == -1;
}

bool json_is_boolean(const struct json *value)
{
	return json_type(value) == JSON_TRI && value->tri_state != -1;
}

bool json_is_number(const struct json *value)
{
	return json_type(value) == JSON_NUMBER;
}

bool json_is_string(const struct json *value)
{
	return json_type(value) == JSON_STRING;
}

bool json_is_array(const struct json *value)
{
	return json_type(value) == JSON_ARRAY;
}

bool json_is_dict(const struct json *value)
{
	return json_type(value) == JSON_DICT;
}

bool json_to_boolean(const struct json *value)
{
	return value->tri_state;
}

double json_to_number(const struct json *value)
{
	return value->number;
}

const char *json_to_string(const struct json *value)
{
	return value->string;
}

struct json *json_null(void)
{
	struct json *value = json_alloc();

	value->tri_state = -1;
	value->type	 = JSON_TRI;

	return value;
}

struct json *json_boolean(bool boolean)
{
	struct json *value = json_alloc();

	value->tri_state = (int)boolean;
	value->type	 = JSON_TRI;

	return value;
}

struct json *json_number(double number)
{
	struct json *value = json_alloc();

	value->number = number;
	value->type   = JSON_NUMBER;

	return value;
}

struct json *json_string(const char *string)
{
	return json_string_acquire(strdup(string));
}

struct json *json_string_acquire(char *string)
{
	struct json *value = json_alloc();

	value->string = string;
	value->type   = JSON_STRING;

	return value;
}

struct json *json_array(void)
{
	struct json *value = json_alloc();

	INIT_LIST_HEAD(&value->children);
	value->type = JSON_ARRAY;

	return value;
}

struct json *json_dict(void)
{
	struct json *value = json_alloc();

	INIT_LIST_HEAD(&value->children);
	value->type  = JSON_DICT;

	return value;
}


static void disown(struct json *child)
{
	if (!list_empty(&child->node)) {
		list_del(&child->node);
	}

	INIT_LIST_HEAD(&child->node);
}

static void adopt(struct json *parent, struct json *child)
{
	list_move(&child->node, &parent->children);
}

int json_array_push(struct json *array, struct json *value)
{
	if (JSON_ARRAY != json_type(array)) {
		return -1;
	}

	adopt(array, value);

	return 0;
}

__pure
static struct json *dict_get(const struct json *dict, const char *label, u64 key)
{
	struct json *it;

	list_for_each_entry(it, &dict->children, node) {
		if (it->hash == key && streq(label, it->label)) {
			return it;
		}
	}

	return NULL;
}

int json_dict_set(struct json *dict, const char *label, struct json *value)
{
	struct json *old;
	u64 hash;

	if (JSON_DICT != json_type(dict)) {
		return -1;
	}

	hash = hash_djb2(label, NULL);

	old = dict_get(dict, label, hash);

	if (old) {
		json_destroy(old);
	}

	if (value->label) {
		free(value->label);
	}

	value->label = strdup(label);
	value->hash  = hash;

	adopt(dict, value);

	return 0;
}

struct json *json_dict_get(const struct json *dict, const char *label)
{
	u64 key;

	if (JSON_DICT != json_type(dict)) {
		return NULL;
	}

	key = hash_djb2(label, NULL);

	return dict_get(dict, label, key);
}

void json_destroy(struct json *value)
{
	disown(value);

	switch (value->type) {
	case JSON_TRI:
	case JSON_NUMBER:
		break;

	case JSON_STRING:
		free(value->string);
		break;

	case JSON_DICT:
	case JSON_ARRAY: {
		struct json *it, *tmp;
		list_for_each_entry_safe(it, tmp, &value->children, node) {
			json_destroy(it);
		}
	} break;
	}

	if (value->label) {
		free(value->label);
	}

	json_free(value);
}

struct json *json_search(const struct json *dict, ... /* NULL */)
{
	va_list ap;
	const char *label;

	va_start(ap, dict);

	while ((const char *)NULL != (label = va_arg(ap, const char *))) {

		if (!dict || !json_type(dict)) {
			return NULL;
		}

		dict = json_dict_get(dict, label);
	}

	return (struct json*)dict;
}

isize do_json_stream(const struct json *value, FILE *fp, bool escape)
{
	isize total;

	total = 0;

	switch (json_type(value)) {

	case JSON_TRI:
		if (value->tri_state == -1) {
			total += fprintf(fp, "null");
		} else if (value->tri_state) {
			total += fprintf(fp, "true");
		} else {
			total += fprintf(fp, "false");
		}
		break;

	case JSON_NUMBER:
		total += fprintf(fp, "%.17g", value->number);
		break;

	case JSON_STRING:
		if (escape) {
			total += fprintf(fp, "\\\"%s\\\"", value->string);
		}
		else {
			total += fprintf(fp, "\"%s\"", value->string);
		}
		break;

	case JSON_ARRAY:
		putc('[', fp);
		{
			struct json *it;

			if (list_empty(&value->children)) {
				goto no_array_children;
			}

			/*
                         * Unfortunately JSON, which claims to be a
                         * language that is human and computer
                         * friendly, does not accept trailling commas.
                         *
                         * This is utterly frustrating.  This is what
                         * happen when you have Web people making
                         * standard.
			 */
			it = list_first_entry(&value->children, struct json, node);

			total += do_json_stream(it, fp, escape);

			list_for_each_entry_continue(it, &value->children, node) {
				putc(',', fp);
				total += do_json_stream(it, fp, escape) + 1;
			}
		} no_array_children:
		putc(']', fp);
		total += 2;
		break;

	case JSON_DICT:
		putc('{', fp);
		{
			struct json *it;

			if (list_empty(&value->children)) {
				goto no_dict_children;
			}

			it = list_first_entry(&value->children, struct json, node);

			if (escape) {
				total += fprintf(fp, "\\\"%s\\\":", it->label);
			} else {
				total += fprintf(fp, "\"%s\":", it->label);
			}

			total += do_json_stream(it, fp, escape);

			list_for_each_entry_continue(it, &value->children, node) {
				if (escape) {
					total += fprintf(fp, ",\\\"%s\\\":", it->label);
				} else {
					total += fprintf(fp, ",\"%s\":", it->label);
				}
				total += do_json_stream(it, fp, escape);
			}
		} no_dict_children:
		putc('}', fp);
		total += 2;
		break;
	}

	return total;
}

void stream_http(const struct json *value, FILE *fp)
{
	switch (json_type(value)) {

	case JSON_TRI:
		if (value->tri_state == -1) {
			fprintf(fp, "4\r\nnull\r\n");
		} else if (value->tri_state) {
			fprintf(fp, "4\r\ntrue\r\n");
		} else {
			fprintf(fp, "5\r\nfalse\r\n");
		}
		break;

	case JSON_NUMBER: {

		/* See https://en.wikipedia.org/wiki/IEEE_754-1985 */
		char buf[24];
		usize len;

		len = snprintf(buf, sizeof(buf), "%.17g", value->number);

		fprintf(fp, "%zX\r\n%s\r\n",
			len, buf);
	}
		break;
	case JSON_STRING:
		fprintf(fp, "%zX\r\n\"%s\"\r\n",
			strlen(value->string) + 2, value->string);
		break;

	case JSON_ARRAY:
		fprintf(fp, "1\r\n[\r\n");
		{
			struct json *it;

			if (list_empty(&value->children)) {
				goto no_array_children;
			}

			/*
			 * Unfortunately JSON, which claims to be a
			 * language that is human and computer
			 * friendly, does not accept trailling commas.
			 *
			 * This is utterly frustrating.  This is what
			 * happen when you have Web people making
			 * standard.
			 */
			it = list_first_entry(&value->children, struct json, node);

			stream_http(it, fp);

			list_for_each_entry_continue(it, &value->children, node) {
				fprintf(fp, "1\r\n,\r\n");
				stream_http(it, fp);
			}
		} no_array_children:
		fprintf(fp, "1\r\n]\r\n");
		break;

	case JSON_DICT:
		fprintf(fp, "1\r\n{\r\n");
		{
			struct json *it;

			if (list_empty(&value->children)) {
				goto no_dict_children;
			}

			it = list_first_entry(&value->children, struct json, node);

			fprintf(fp, "%zX\r\n\"%s\":\r\n", strlen(it->label) + 3,
				it->label);

			stream_http(it, fp);

			list_for_each_entry_continue(it, &value->children, node) {
				fprintf(fp, "%zX\r\n,\"%s\":\r\n", strlen(it->label) + 4,
					it->label);
				stream_http(it, fp);
			}
		} no_dict_children:
		fprintf(fp, "1\r\n}\r\n");
		break;
	}
}


isize json_stream(const struct json *value, FILE *fp)
{
	return do_json_stream(value, fp, false);
}

void json_stream_http(const struct json *value, FILE *fp)
{
	stream_http(value, fp);
	fprintf(fp, "0\r\n\r\n");
}

char *json_dostringify(const struct json *value, bool escape)
{
	FILE *stream;
	char *buf;
	usize length;

	stream = open_memstream(&buf, &length);

	do_json_stream(value, stream, escape);

	fclose(stream);

	return buf;
}

isize json_streamfd(const struct json *value, int fd)
{
	FILE *fp;
	int dup_fd;
	isize size;

	dup_fd = dup(fd);

	if (dup_fd < 0) {
		return -1;
	}

	fp = fdopen(dup_fd, "wb");

	if (!fp) {
		return -1;
	}

	size = json_stream(value, fp);

	fclose(fp);

	return size;
}
