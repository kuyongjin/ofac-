import requests
import pandas as pd
import os

# 깃허브 금고(Secrets)에 숨겨둔 API 키를 불러옴
API_KEY = os.environ.get("ETHERSCAN_API_KEY")

# USDT 스마트 컨트랙트 주소 및 블랙리스트 추가(AddedBlacklist) 이벤트 해시값
CONTRACT_ADDRESS = "0xdac17f958d2ee523a2206206994597c13d831ec7"
TOPIC0 = "0x42e16015ba322c3fb66dc543b5932ef910047b311fc1953eb6c342f5ed727782"

def main():
    if not API_KEY:
        print("에러: 이더스캔 API 키가 없습니다. 깃허브 Secrets를 확인하세요.")
        return

    print("USDT 온체인 블랙리스트 수집 중...")
    
    # 이더스캔 API 호출 URL 구성
    url = f"https://api.etherscan.io/api?module=logs&action=getLogs&fromBlock=0&toBlock=latest&address={CONTRACT_ADDRESS}&topic0={TOPIC0}&apikey={API_KEY}"
    
    response = requests.get(url).json()
    
    if response.get("status") == "1":
        wallets = []
        for item in response["result"]:
            # 데이터에서 지갑 주소 부분만 파싱 (앞의 0들 제거하고 0x 붙이기)
            raw_address = item.get("data", "")
            if len(raw_address) >= 40:
                clean_address = "0x" + raw_address[-40:]
                wallets.append(["USDT(테더사 동결지갑)", clean_address.lower()])
        
        # 데이터프레임 변환 및 중복 제거
        df = pd.DataFrame(wallets, columns=["코인명(온체인)", "지갑주소"])
        df = df.drop_duplicates().sort_values(by=["지갑주소"])
        
        # 고정 파일명으로 저장 (덮어쓰기)
        output_name = "usdt_blacklist_addresses.csv"
        df.to_csv(output_name, index=False, encoding='utf-8-sig')
        print(f"성공: {len(df)}개 USDT 동결 지갑 추출 완료 ({output_name} 저장)")
        else:
        print(f"API 호출 실패: {response.get('message')} / 상세내용: {response.get('result')}")

if __name__ == "__main__":
    main()
