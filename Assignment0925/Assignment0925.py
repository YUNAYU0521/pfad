import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

headers = {
    'User-Agent': 'python-requests/2.32.3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': '*/*',
    'Connection': 'keep-alive'
}

url = 'https://www.hko.gov.hk/tide/cCLKtext2024.html'
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    data = []

    for row in soup.select('table tr'):
        cols = row.find_all('td')
        if len(cols) > 0:
            date = cols[0].text.strip() + '-' + cols[1].text.strip()
            tide_level = cols[2].text.strip()
            if tide_level:  
                data.append({'Date': date, 'Tide Level': float(tide_level)})

    df = pd.DataFrame(data[::10])
    df = df.dropna()  

    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Tide Level'], marker='o', linestyle='-', color='b', markersize=5)
    plt.title('Tide Levels over Time')
    plt.xlabel('Date')
    plt.ylabel('Tide Level (cm)')
    plt.xticks(rotation=45)
    plt.grid(visible=True)
    plt.tight_layout()
    plt.show()
else:
    print(f"请求失败，状态码：{response.status_code}")