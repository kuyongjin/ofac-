import requests
import pandas as pd
import re

def is_valid_eth_address(address):
    # 이더리움 지갑 주소 정규식 (0x로 시작하고 뒤에 40자리의 16진수)
    pattern = re.compile(r'^0x[a-fA-F0-9]{40}$')
    return bool(pattern.match(address))

def main():
    print("글로벌 위험 지갑 리스트 정밀 수집 시작...")
    raw_data = []

    # 소스 1: CryptoscamDB (URL과 주소가 섞여 있음)
    try:
        url_1 = "https://raw.githubusercontent.com/CryptoScamDB/blacklist/master/addresses.json"
        res = requests.get(url_1).json()
        for item in res:
            # item 자체가 주소 문자열인 경우와 객체인 경우 모두 대응
            addr = item if isinstance(item, str) else item.get('address', '')
            if is_valid_eth_address(addr):
                raw_data.append(["Scam/Fraud", addr.lower()])
    except: print("! 소스 1 수집 실패")

    # 소스 2: MyEtherWallet (주로 지갑 주소 위주)
    try:
        url_2 = "https://raw.githubusercontent.com/MyEtherWallet/ethereum-lists/master/src/addresses/blacklisted-addresses.json"
        res = requests.get(url_2).json()
        for item in res:
            addr = item.get('address', '')
            if is_valid_eth_address(addr):
                raw_data.append(["Hacker/Malicious", addr.lower()])
    except: print("! 소스 2 수집 실패")

    # 소스 3: ScamSniffer (최신 피싱 지갑 리스트)
    try:
        url_3 = "https://raw.githubusercontent.com/scamsniffer/scam-database/main/blacklist/combined.json"
        res = requests.get(url_3).json()
        for addr in res:
            if is_valid_eth_address(addr):
                raw_data.append(["Phishing", addr.lower()])
    except: print("! 소스 3 수집 실패")

    # 데이터 정리 및 저장
    if raw_data:
        df = pd.DataFrame(raw_data, columns=["위험분류", "지갑주소"])
        df = df.drop_duplicates(subset=['지갑주소']).sort_values(by="위험분류")
        
        output_name = "malicious_addresses.csv"
        df.to_csv(output_name, index=False, encoding='utf-8-sig')
        print(f"✅ 필터링 완료: 총 {len(df)}개의 유효한 지갑 주소 추출 성공!")
    else:
        print("❌ 유효한 지갑 주소를 찾지 못했습니다.")

if __name__ == "__main__":
    main()
