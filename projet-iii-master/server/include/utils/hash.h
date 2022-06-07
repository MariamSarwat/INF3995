#ifndef HASH_H
#define HASH_H

/* See <http://www.cse.yorku.ca/~oz/hash.html> */

static inline u64 hash_djb2(const char *str, usize *len)
{
	int c;
	const char *diff;
	u64 hash;

	diff = str;
	hash = 5381;

	while ((c = (int)*str)) {
		hash = ((hash << 5) + hash) ^ c;
		++str;
	}

	if (len) {
		*len = str - diff;
	}

	return hash;
}

__pure
static inline u64 hash_djb2_n(const char *str, usize len)
{
	u64 hash;

	hash = 5381;

	for (usize i=0; i<len; ++i) {
		hash = ((hash << 5) + hash) ^ str[i];
	}

	return hash;
}

__pure
static inline u64 hash_djb2_continue(const char *str, u64 prev_hash)
{
	int c;
	u64 hash;

	hash = prev_hash;

	while ((c = (int)*str)) {
		hash = ((hash << 5) + hash) ^ c;
		++str;
	}

	return hash;
}


#endif
