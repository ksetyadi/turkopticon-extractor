import requests
import re
import collections

GET_REQUESTERS_IDS_URL = 'https://turkopticon.ucsd.edu/requesters?order=updated_at+DESC&page={0}'
GET_REQUESTERS_DETAIL_URL = 'http://turkopticon.ucsd.edu/api/multi-attrs.php?ids={0}'
TURKOPTICON_PAGE = 31
IDS_PER_CHUNK = 20

def extract_requesters_id(st):
	ids = []
	couples = [m.start() for m in re.finditer('reports\?id=', st)]

	for c in couples:
		end_pos = st.find('"', c)
		requester_id = st[c + 11: end_pos]
		ids.append(requester_id)

	return ids

def get_requesters_detail(requesters_ids):	
	# ids should be in chunks with each chunk ~ 20 ids
	# write the final result by requesting through API
	with open('result_final.txt', 'w') as f:
		dq_ids = collections.deque(requesters_ids)

		while len(dq_ids) > 0:
			twenty_ids = []

			for i in range(0, IDS_PER_CHUNK):
				if len(dq_ids) > 0:
					twenty_ids.append(dq_ids.popleft())

			params = ','.join(twenty_ids)
			url = GET_REQUESTERS_DETAIL_URL.format(params,)
			r = requests.get(url)

			if r.status_code == 200:
				results = r.json()
				keys = results.keys()

				for key in keys:
					try:
						strtowrite = '{0}, {1}, {2}, {3}, {4}, {5}, {6}'.format(key, \
							results[key]['name'], results[key]['attrs']['comm'], \
							results[key]['attrs']['pay'], results[key]['attrs']['fair'], \
							results[key]['attrs']['fast'], results[key]['reviews'])
					except UnicodeEncodeError, e:
						continue
					f.write(strtowrite + '\n')

def main(url):
	requesters_ids = []

	for p in range(1, TURKOPTICON_PAGE):
		print 'Getting page {0}...'.format(p,)
		current_url = url.format(p,)
		r = requests.get(current_url)
		ids = extract_requesters_id(r.text)
		requesters_ids += ids

	# write the raw result
	with open('result.txt', 'w') as f:
		for rqid in requesters_ids:
			f.write(rqid + '\n')

		f.write('\n\nTotal ID: ' + str(len(requesters_ids)) + '\n')

	get_requesters_detail(requesters_ids)

if __name__ == '__main__':
	url = GET_REQUESTERS_IDS_URL
	main(url)
