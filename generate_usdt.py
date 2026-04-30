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
    
    try:
        # 1. 현재 최신 블록 번호를 16진수로 가져와서 10진수로 변환
        block_url = f"https://api.etherscan.io/v2/api?chainid=1&module=proxy&action=eth_blockNumber&apikey={API_KEY}"
        block_response = requests.get(block_url).json()
        current_block_hex = block_response.get("result", "0x0")
        current_block = int(current_block_hex, 16)
        
        # 2. 약 100,000 블록 전부터 조회 (약 2주 분량)
        # V2 무료 티어는 조회 범위가 너무 넓으면 데이터를 안 주므로 범위를 좁히는 것이 핵심
        from_block = current_block - 100000
        
        print(f"현재 블록: {current_block}, 조회 시작 블록: {from_block}")

        # 3. 로그 수집 API 호출
        url = f"https://api.etherscan.io/v2/api?chainid=1&module=logs&action=getLogs&fromBlock={from_block}&toBlock=latest&address={CONTRACT_ADDRESS}&topic0={TOPIC0}&apikey={API_KEY}"
        response = requests.get(url).json()
        
        if response.get("status") == "1":
            wallets = []
            for item in response["result"]:
                raw_address = item.get("data", "")
                if len(raw_address) >= 40:
                    clean_address = "0x" + raw_address[-40:]
                    wallets.append(["USDT(테더사 동결지갑)", clean_address.lower()])
            
            df = pd.DataFrame(wallets, columns=["코인명(온체인)", "지갑주소"])
            df = df.drop_duplicates().sort_values(by=["지갑주소"])
            
            output_name = "usdt_blacklist_addresses.csv"
            df.to_csv(output_name, index=False, encoding='utf-8-sig')
            print(f"성공: {len(df)}개 USDT 신규 동결 지갑 추출 완료 ({output_name} 저장)")
        else:
            # 데이터가 없는 경우(No records found)도 정상적인 결과로 처리
            print(f"알림: {response.get('message')} (최근 2주 내 신규 동결 지갑 없음)")
            # 파일이 없으면 에러가 나므로, 빈 파일이라도 생성
            if not os.path.exists("usdt_blacklist_addresses.csv"):
                pd.DataFrame(columns=["코인명(온체인)", "지갑주소"]).to_csv("usdt_blacklist_addresses.csv", index=False)

    except Exception as e:
        print(f"시스템 에러 발생: {e}")

if __name__ == "__main__":
    main()
