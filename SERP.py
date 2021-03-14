from urllib.parse import urlparse, quote
import requests
from bs4 import BeautifulSoup
import time
from pandas import read_excel
import threading
"""

What we are doing here is searching terms, by forming the urls and extracting links and titles from the 
google's first page results.

rest are just string manipulation
splitting the urls and checking for condition that would satisfy the needs.

Note: Check for the initial div class to strip the links google changes things periodically

"""




def extract_link_n_title(url):
	results  = []
	USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
	headers = {"user-agent": USER_AGENT}
	resp = requests.get(url, headers=headers)
	if resp.status_code == 200:
	    soup = BeautifulSoup(resp.content, "html.parser")
	    for i in soup.find_all('div', class_='g'):
	    	a_tags = i.find_all('a')
	    	if a_tags:
	        	link = a_tags[0]['href']
	        	if i.find('h3').text is not None:
	        		title = i.find('h3').text
	        	else:
	        		title = 'some_Random_title'
	        	results.append({
	        	'title':title,
	        	'link' : link
	        	})

	return results
			


def search_resume(d_name, c_name, r_name):
	co_name = c_name.split()[0].lower() + ' ' + c_name.split()[1].lower()
	matches = ['lebenslauf','Lebenslauf','cv', 'curriculum', 'resume', 'vita', 'vitae']
	url_manipulation = quote(f"'{d_name}'+'{co_name}'+'lebenslauf'+ext:pdf")
	URL = f"https://google.com/search?q={url_manipulation}"
	for i in extract_link_n_title(URL):
		name_in_url_split = urlparse(i['link']).path.split('/')[-1].lower()
		dir_name = d_name.split()[0].lower()
		if any(x in i['link'] for x in matches):
			with open('results1.txt', 'a') as file:
				file.write( d_name +' '+ c_name + ' ' + r_name + '  -->'+ i['link']+'\n')
		elif dir_name in name_in_url_split:
			with open('results1.txt', 'a') as file:
				file.write( d_name +' '+ c_name + ' ' + r_name  + '  -->'+ i['link']+'\n')
	else:
		with open('results1.txt', 'a') as file:
				file.write(d_name + ' ' + c_name + ' ' + r_name   + '  No resume match found\n' )





def search_primary(d_name, c_name, r_name):
	co_name = c_name.split()[0].lower() + ' ' + c_name.split()[1].lower()
	url_manipulation = quote(f"'{d_name}'+'{co_name}'+ext:pdf")
	URL = f"https://google.com/search?q={url_manipulation}"
	comp_name = c_name.split()[0].lower()
	for i in extract_link_n_title(URL):
		if comp_name in domain_parse(i['link']):
			with open('results1.txt', 'a') as file:
				file.write( d_name+' '+ c_name + ' ' + r_name + '  -->'+ i['link']+'\n')
	else:
		with open('results1.txt', 'a') as file:
				file.write(d_name + ' ' + c_name +' ' + r_name + '  No primary match found\n')



def domain_parse(link):
	result = urlparse(link).netloc
	return result.split('.')[-2]


def write_to_file(incoming):
	with open('results1.txt', 'a') as file:
		file.write(f'{incoming}')


def search_linkedin(d_name, c_name, r_name):
	co_name = c_name.split()[0].lower() + ' ' + c_name.split()[1].lower()
	url_manipulation = quote(f"'{d_name}'+'{co_name}'+site:linkedin.com")
	URL = f"https://google.com/search?q={url_manipulation}"
	for i in extract_link_n_title(URL):
		linkedin_name = urlparse(i['link']).path.split('/')[-1]
		dir_name = d_name.split()[0].lower()
		if (domain_parse(i['link']) == 'linkedin') and (dir_name in linkedin_name):
			with open('results1.txt', 'a') as file:
				file.write( d_name+' '+ c_name +' ' + r_name + '  -->'+ i['link'] +'\n')
	else:
		with open('results1.txt', 'a') as file:
				file.write(d_name + ' ' + c_name +' ' + r_name + '  No linkdein match found \n' )



def general_search_bio(d_name, c_name, r_name):
	co_name = c_name.split()[0].lower() + ' ' + c_name.split()[1].lower()
	comp_name = c_name.split()[0].lower()
	url_manipulation = quote(f"'{d_name}'+'{co_name}'")
	URL = f"https://google.com/search?q={url_manipulation}"
	for i in extract_link_n_title(URL):
		if comp_name in domain_parse(i['link']):
			with open('results1.txt', 'a') as file:
				file.write( d_name+' '+ c_name + ' ' + r_name +'  -->'+ i['link']+'\n')
	else:
		with open('results1.txt', 'a') as file:
				file.write(d_name + ' ' + c_name +' ' + r_name + '  No normal primary match found\n')



def initiator():
	start = time.perf_counter()
	for items in key_purse:
		try:
			t1 = threading.Thread(target=search_resume, args =[items['director_name'], items['company_name'], items['role_name']])
			t1.start()
			t2 = threading.Thread(target=search_linkedin, args =[items['director_name'], items['company_name'], items['role_name']])
			t2.start()
			t3 = threading.Thread(target=search_primary, args =[items['director_name'], items['company_name'], items['role_name']])
			t3.start()
			t4 = threading.Thread(target=general_search_bio, args =[items['director_name'], items['company_name'], items['role_name']])
			t4.start()
			write_to_file('\n****************\n')
			t1.join()
			t2.join()
			t3.join()
			t4.join()
		except:
			pass
	elapsed = time.perf_counter() - start
	print(f'Time taken is {elapsed:0.2f} seconds!')
			           


def preworks(index_start, index_end, file_name , sheet ):
	df = read_excel(file_name, sheet)
	d_name = df['Director Name'].tolist()
	c_name = df['Company Name'].tolist()
	r_name = df['Role Name'].tolist()
	global key_purse
	# key_purse = dict(zip(d_name[index_start:index_end],c_name[index_start:index_end]))
	key_purse = []
	for dir_name, comp_name, role_name in zip(d_name[index_start:index_end], c_name[index_start:index_end], r_name[index_start:index_end]):
		key_purse.append(
			{
			'director_name' : dir_name,
			'company_name' : comp_name,
			'role_name' : role_name
			})
	return None



if __name__ =='__main__':
	file_name = input('please enter the file name: ') 
	sheet = input('please enter the sheet number: ')
	sheet = 'Sheet'+ str(sheet)
	index_start = int(input('please enter the starting index: '))
	index_end = int(input('please enter the ending index: '))
	preworks(index_start, index_end, file_name= 'prof_chek1.xlsx', sheet='Sheet4')
	initiator()



