import base64
import re
import unittest

import requests

base_url = 'http://localhost:8080/index.php/apps/files/upload'
base_headers = {
	'Authorization': f'Basic {base64.b64encode('admin:admin'.encode('utf-8')).decode('utf-8')}',
	'Upload-Draft-Interop-Version': '6',
}

location_regex = f'^{re.escape(base_url)}/[a-z0-9.]+$'


class ResumableUpload(unittest.TestCase):
	def test_create(self):
		response = requests.post(base_url, 'abc', headers=base_headers | {'Upload-Complete': '1', 'Upload-Length': '3'})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.headers['Upload-Complete'], '1')
		self.assertEqual(response.headers['Upload-Offset'], '3')
		self.assertRegex(response.headers['Location'], location_regex)

		response = requests.head(response.headers['Location'], headers=base_headers)
		self.assertEqual(response.status_code, 204)
		self.assertEqual(response.headers['Upload-Complete'], '1')
		self.assertEqual(response.headers['Upload-Offset'], '3')
		self.assertEqual(response.headers['Upload-Length'], '3')
		self.assertRegex(response.headers['Cache-Control'], 'no-store')

	def test_create_empty_complete(self):
		response = requests.post(base_url, headers=base_headers | {'Upload-Complete': '1', 'Upload-Length': '0'})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.headers['Upload-Complete'], '1')
		self.assertEqual(response.headers['Upload-Offset'], '0')
		self.assertRegex(response.headers['Location'], location_regex)

	def test_create_empty_incomplete(self):
		response = requests.post(base_url, headers=base_headers | {'Upload-Complete': '0', 'Upload-Length': '0'})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.headers['Upload-Complete'], '0')
		self.assertEqual(response.headers['Upload-Offset'], '0')
		self.assertRegex(response.headers['Location'], location_regex)

	def test_append_completed(self):
		response = requests.post(base_url, 'abc', headers=base_headers | {'Upload-Complete': '1', 'Upload-Length': '3'})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.headers['Upload-Complete'], '1')
		self.assertEqual(response.headers['Upload-Offset'], '3')
		self.assertRegex(response.headers['Location'], location_regex)

		response = requests.patch(response.headers['Location'], 'def', headers=base_headers | {'Content-Type': 'application/partial-upload', 'Upload-Complete': '1'})
		self.assertEqual(response.status_code, 400)
		self.assertEqual('Upload-Complete' not in response.headers, True)
		self.assertEqual(response.headers['Upload-Offset'], '3')
		self.assertEqual('Location' not in response.headers, True)
		self.assertEqual(response.headers['Content-Type'], 'application/problem+json')
		self.assertEqual(response.json(), {
			'type': 'https://iana.org/assignments/http-problem-types#completed-upload',
			'title': 'upload is already completed',
		})

	def test_append_non_existent(self):
		response = requests.patch(f'{base_url}/test', 'abc', headers=base_headers | {'Content-Type': 'application/partial-upload', 'Upload-Complete': '1'})
		self.assertEqual(response.status_code, 404)
		self.assertEqual('Upload-Complete' not in response.headers, True)
		self.assertEqual('Upload-Offset' not in response.headers, True)
		self.assertEqual('Location' not in response.headers, True)

	def test_create_wrong_upload_length(self):
		response = requests.post(base_url, 'abc', headers=base_headers | {'Upload-Complete': '1', 'Upload-Length': '4'})
		self.assertEqual(response.status_code, 400)
		self.assertEqual('Upload-Complete' not in response.headers, True)
		self.assertEqual('Upload-Offset' not in response.headers, True)
		self.assertEqual('Location' not in response.headers, True)

	def test_append(self):
		response1 = requests.post(base_url, 'abc', headers=base_headers | {'Upload-Complete': '0', 'Upload-Length': '9'})
		self.assertEqual(response1.status_code, 201)
		self.assertEqual(response1.headers['Upload-Complete'], '0')
		self.assertEqual(response1.headers['Upload-Offset'], '3')
		self.assertRegex(response1.headers['Location'], location_regex)

		response2 = requests.head(response1.headers['Location'], headers=base_headers)
		self.assertEqual(response2.status_code, 204)
		self.assertEqual(response2.headers['Upload-Complete'], '0')
		self.assertEqual(response2.headers['Upload-Offset'], '3')
		self.assertEqual(response2.headers['Upload-Length'], '9')
		self.assertRegex(response2.headers['Cache-Control'], 'no-store')

		response2 = requests.patch(response1.headers['Location'], 'def', headers=base_headers | {'Content-Type': 'application/partial-upload', 'Upload-Complete': '0', 'Upload-Offset': response1.headers['Upload-Offset']})
		self.assertEqual(response2.status_code, 201)
		self.assertEqual(response2.headers['Upload-Complete'], '0')
		self.assertEqual(response2.headers['Upload-Offset'], '6')
		self.assertEqual('Location' not in response2.headers, True)

		response2 = requests.head(response1.headers['Location'], headers=base_headers)
		self.assertEqual(response2.status_code, 204)
		self.assertEqual(response2.headers['Upload-Complete'], '0')
		self.assertEqual(response2.headers['Upload-Offset'], '6')
		self.assertEqual(response2.headers['Upload-Length'], '9')
		self.assertRegex(response2.headers['Cache-Control'], 'no-store')

		response2 = requests.patch(response1.headers['Location'], 'ghi', headers=base_headers | {'Content-Type': 'application/partial-upload', 'Upload-Complete': '1', 'Upload-Offset': response2.headers['Upload-Offset']})
		self.assertEqual(response2.status_code, 201)
		self.assertEqual(response2.headers['Upload-Complete'], '1')
		self.assertEqual(response2.headers['Upload-Offset'], '9')
		self.assertEqual('Location' not in response2.headers, True)

		response2 = requests.head(response1.headers['Location'], headers=base_headers)
		self.assertEqual(response2.status_code, 204)
		self.assertEqual(response2.headers['Upload-Complete'], '1')
		self.assertEqual(response2.headers['Upload-Offset'], '9')
		self.assertEqual(response2.headers['Upload-Length'], '9')
		self.assertRegex(response2.headers['Cache-Control'], 'no-store')

	def test_append_wrong_upload_length(self):
		response1 = requests.post(base_url, 'abc', headers=base_headers | {'Upload-Complete': '0', 'Upload-Length': '10'})
		self.assertEqual(response1.status_code, 201)
		self.assertEqual(response1.headers['Upload-Complete'], '0')
		self.assertEqual(response1.headers['Upload-Offset'], '3')
		self.assertRegex(response1.headers['Location'], location_regex)

		response2 = requests.patch(response1.headers['Location'], 'def', headers=base_headers | {'Content-Type': 'application/partial-upload', 'Upload-Complete': '0', 'Upload-Offset': response1.headers['Upload-Offset']})
		self.assertEqual(response2.status_code, 201)
		self.assertEqual(response2.headers['Upload-Complete'], '0')
		self.assertEqual(response2.headers['Upload-Offset'], '6')
		self.assertEqual('Location' not in response2.headers, True)

		response2 = requests.patch(response1.headers['Location'], 'ghi', headers=base_headers | {'Content-Type': 'application/partial-upload', 'Upload-Complete': '1', 'Upload-Offset': response2.headers['Upload-Offset']})
		self.assertEqual(response2.status_code, 400)
		self.assertEqual('Upload-Complete' not in response2.headers, True)
		self.assertEqual(response2.headers['Upload-Offset'], '9')
		self.assertEqual('Location' not in response2.headers, True)

	def test_append_wrong_upload_offset(self):
		response = requests.post(base_url, 'abc', headers=base_headers | {'Upload-Complete': '0', 'Upload-Length': '10'})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.headers['Upload-Complete'], '0')
		self.assertEqual(response.headers['Upload-Offset'], '3')
		self.assertRegex(response.headers['Location'], location_regex)

		response = requests.patch(response.headers['Location'], 'def', headers=base_headers | {'Content-Type': 'application/partial-upload', 'Upload-Complete': '0', 'Upload-Offset': '1'})
		self.assertEqual(response.status_code, 409)
		self.assertEqual('Upload-Complete' not in response.headers, True)
		self.assertEqual(response.headers['Upload-Offset'], '3')
		self.assertEqual('Location' not in response.headers, True)
		self.assertEqual(response.headers['Content-Type'], 'application/problem+json')
		self.assertEqual(response.json(), {
			'type': 'https://iana.org/assignments/http-problem-types#mismatching-upload-offset',
			'title': 'offset from request does not match offset of resource',
			'expected-offset': 3,
			'provided-offset': 1,
		})

if __name__ == '__main__':
	unittest.main()
