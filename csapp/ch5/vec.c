#include <stdio.h>

//typedef long data_t;
typedef double data_t;

typedef struct {
	long len;
	data_t *data;
} vec_rec, *vec_ptr;

//#define IDENT 0
//#define OP +

#define IDENT 1
#define OP *

vec_ptr new_vec(long len)
{
	vec_ptr result = (vec_ptr) malloc(sizeof(vec_rec));
	data_t *data = NULL;
	if (!result)
		return NULL;
	result->len = len;

	if (len > 0) {
		data = (data_t*)calloc(len, sizeof(data_t));
		if  (!data) {
			free((void*) result);
			return NULL;
		}
	}

	result->data = data;
	return result;
}

int get_vec_element(vec_ptr v, long index, data_t *dest)
{
	if (index < 0 || index >= v->len)
		return 0;
	*dest = v->data[index];
	return 1;
}

data_t *get_vec_start(vec_ptr v)
{
	return v->data;
}

long vec_length(vec_ptr v)
{
	return v->len;
}


void combine1(vec_ptr v, data_t *dest)
{
	long i;

	*dest = IDENT;
	for (i=0; i<vec_length(v); i++) {
		data_t val;
		get_vec_element(v, i, &val);
		*dest = *dest OP val;
	}
}

void combine2(vec_ptr v, data_t *dest)
{
	long i;
	long length = vec_length(v);
	
	*dest = IDENT;
	for (i=0; i<length; i++) {
		data_t val;
		get_vec_element(v, i, &val);
		*dest = *dest OP val;
	}
}

void combine3(vec_ptr v, data_t *dest)
{
	long i;
	long length = vec_length(v);
	data_t *data = get_vec_start(v);
	
	*dest = IDENT;
	for (i=0; i<length; i++) {
		*dest = *dest OP data[i];
	}
}

void combine4(vec_ptr v, data_t *dest)
{
	long i;
	long length = vec_length(v);
	data_t *data = get_vec_start(v);
	data_t acc = IDENT;
	
	for (i=0; i<length; i++) {
		acc = acc OP data[i];
	}
	*dest = acc;
}


int main()
{
}
