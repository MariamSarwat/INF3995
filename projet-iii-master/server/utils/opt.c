/*
 * SPDX-License-Identifier: GPL-2.0-or-later
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "utils/opt.h"

static int cmp_opt_key(const void *key, const void *mem)
{
	const struct opt *opt = mem;
	return strcmp(key, opt->name);
}

static int cmp_opt(const void *A, const void *B)
{
	const struct opt *opt_A = A;
	const struct opt *opt_B = B;

	return strcmp(opt_A->name, opt_B->name);
}

static inline struct opt *find_opt(const char *str, struct opt *options, usize len)
{
	return bsearch(str, options, len, sizeof(struct opt), cmp_opt_key);
}

int do_opt(int at, char **argv, struct opt *options, usize len)
{
	int ret;
	char *arg;
	char *nxt;
	struct opt *opt;

	ret = 0;
	arg = argv[at] + 1;
	nxt = NULL;

	for (usize i=0; ; ++i) {
		char c = arg[i];

		switch (c) {
		case '=':
			arg[i] = '\0';
			nxt    = arg + i + 1;
			__fallthrough;
		case '\0':
			goto end_of_arg;
		}
	}
end_of_arg:

	opt = find_opt(arg, options, len);

	if (!opt) {
		fprintf(stderr, "Invalid option '%s'\n", arg);
		return -1;
	}

	if (OPT_FLG == opt->type) {
		*(opt->flg) = true;
		goto no_arg;
	}

	if (OPT_CLB == opt->type) {
		(*(opt->clb))();
		goto no_arg;
	}

	if (NULL == nxt) {
		nxt = argv[at + 1];
		ret = 1;
	}

	if (NULL == nxt) {
		fprintf(stderr, "Missing argument for option '%s'\n", opt->name);
		return -1;
	}

	switch (opt->type) {
	case OPT_INT:
		*(opt->num) = atoi(nxt);
		break;
	case OPT_STR:
		*(opt->str) = nxt;
		break;
	}

no_arg:
	return ret;
}

__flatten
int opt_parse(int argc, char **argv, struct opt *options, usize len)
{
	int args_count = 1;

	qsort(options, len, sizeof(struct opt), cmp_opt);

	for (int i=1; i<argc; ++i) {

		char *arg = argv[i];

		/* Argument? */
		if ('-' != arg[0]) {
			argv[args_count++] = arg;
			continue;
		}

		/* Option? */
		if ('-' != arg[1]) {

			int ret = do_opt(i, argv, options, len);

			if (ret < 0) {
				return -args_count;
			}

			i += ret;
			continue;
		}

		/* End of option -- */
		break;
	}

	return args_count;
}

void opt_usage(const char *usage, struct opt *options, usize len)
{
	usize gt_len = 0;

	for (usize i=0; i<len; ++i) {
		usize tmp = strlen(options[i].name);
		if (tmp > gt_len) {
			gt_len = tmp;
		}
	}

	puts(usage);
	for (usize i=0; i<len; ++i) {
		struct opt *opt = &options[i];

		printf("\t -%-*s\t%s\n",
		       (int)gt_len, opt->name,
		       opt->help);
	}
}
