struct Node {
	int index;
	int jamo_seq_len;
	uint16_t *jamo_seq;
	uint16_t jamo_code;
	uint16_t pua_code;
	int childrenLen;
	struct Node** children;
	const char* node_name;
};


struct Translator {
	struct Node *node;
};


void hypua_jc2p_translator_init(void *translator);
void hypua_jd2p_translator_init(void *translator);
int hypua_jc2p_translator_getstate(void *translator);
int hypua_jc2p_translator_setstate(void *translator, int state);
