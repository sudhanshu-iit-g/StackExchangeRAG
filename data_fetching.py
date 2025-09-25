import re
import requests

def clean_query(query):
    return re.sub(r'[\\/*?:"<>|]', "", query)

def build_payload(query, start=1, num=10, site='math', sort='relevance', order='desc', **params):
    payload = {
        'q': query,
        'page': start,
        'pagesize': num,
        'site': site,
        'sort': sort,
        'order': order
    }
    payload.update(params)
    return payload

def make_request(payload):
    response = requests.get('https://api.stackexchange.com/2.3/search/advanced', params=payload)
    if response.status_code != 200:
        raise Exception(f'Request failed with status code {response.status_code}. Response: {response.text}')
    return response.json()

def extract_question_ids(response_data):
    ids = []
    for item in response_data['items']:
        q_id = item['question_id']
        ids.append(str(q_id)) 
    return ids

def get_question_ids(query, result_total=10, site='math.stackexchange'):
    question_ids = []
    page = 1
    page_size = 100  

    while len(question_ids) < result_total:
        payload = build_payload(query, start=page, num=min(page_size, result_total - len(question_ids)), site=site)
        response = make_request(payload)
        
        new_ids = extract_question_ids(response)
        question_ids.extend(new_ids)
        
        if len(new_ids) < page_size or 'has_more' not in response or not response['has_more']:
            break
        
        page += 1

    return question_ids

def fetch_and_process_answers(question_ids):
    from text_processing import process_answer_text
    
    processed_answers = []
    para = {
        'order': 'desc',
        'sort': 'activity',
        'site': 'math',
        'filter': '!*SU8CGYZitCB.D*(BDVIficKj7nFMLLDij64nVID)N9aK3GmR9kT4IzT*5iO_1y3iZ)6W.G*'
    }
    for id in question_ids:
        api_url = f'https://api.stackexchange.com/2.3/questions/{id}/answers'
        response = requests.get(api_url, params=para)
        if response.status_code == 200:
            data = response.json()
            for answer in data['items']:
                html_content = answer['body']
                processed_text = process_answer_text(html_content)
                processed_answers.append(processed_text)
        else:
            print(f"Error fetching answers for question {id}: {response.status_code}")
    return processed_answers