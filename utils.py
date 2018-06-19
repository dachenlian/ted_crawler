def compare_times(talk, show_total_lines=True, show_sample_lines=False, show_time_differences=False):
	tw = talk['transcripts']['zh-tw']
	cn = talk['transcripts']['zh-cn']
	tw_trans = []
	cn_trans = []
	for lang, trans in [(tw, tw_trans), (cn, cn_trans)]:
		for para in lang['paragraphs']:
			for line in para['cues']:
				trans.append((line['time'], line['text']))

	if show_total_lines:
		print(f"Total number of lines in \"{talk['title']}\"\nTW:{len(tw_trans)}\tCN:{len(cn_trans)}")
	
	if show_sample_lines:
		print("=" * 40)
		for i in range(5):
			print("TW", tw_trans[i][1])
			print("CN", cn_trans[i][1])
	
	if show_time_differences:
		print("=" * 40)
		print("Differences in time:")
		for tw, cn in zip(tw_trans, cn_trans):
			print(abs(tw[0] - cn[0]), tw[1], cn[1], sep="|")


