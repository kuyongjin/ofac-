import xml.etree.ElementTree as ET
import pandas as pd
import os

# 파일 경로 및 네임스페이스 설정
xml_file = "SDN_ADVANCED.XML"
namespace = {'sdn': 'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ADVANCED_XML'}

def main():
    print("데이터 분석 중...")
    if not os.path.exists(xml_file):
        print(f"에러: {xml_file} 파일이 없습니다.")
        return

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 코인 심볼과 ID 매핑 추출
    feature_map = {}
    for ftv in root.findall(".//sdn:FeatureTypeValues/sdn:FeatureType", namespace):
        ft_id = ftv.attrib.get('ID')
        ft_text = ftv.text
        if ft_text and "Digital Currency Address - " in ft_text:
            asset_name = ft_text.replace("Digital Currency Address - ", "").strip()
            feature_map[ft_id] = asset_name

    # 데이터 추출
    all_data = []
    for feature in root.findall(".//sdn:Feature", namespace):
        ft_id = feature.attrib.get('FeatureTypeID')
        if ft_id in feature_map:
            coin_symbol = feature_map[ft_id]
            # A열 내용을 "코인명(ofac제재지갑)" 형식으로 강제 지정
            coin_display_name = f"{coin_symbol}(ofac제재지갑)"
            
            for version_detail in feature.findall(".//sdn:VersionDetail", namespace):
                address = version_detail.text
                if address:
                    all_data.append([coin_display_name, address])

    # 데이터프레임 변환 (헤더 이름도 요청하신 대로 설정)
    df = pd.DataFrame(all_data, columns=["코인명(ofac제재지갑)", "지갑주소"])
    
    # 중복 제거 및 정렬
    df = df.drop_duplicates().sort_values(by=["코인명(ofac제재지갑)", "지갑주소"])

    # CSV 파일로 저장
    output_name = "ofac_sanctioned_addresses.csv"
    df.to_csv(output_name, index=False, encoding='utf-8-sig')
    print(f"성공: {len(df)}개 주소 추출 완료 -> {output_name}")

if __name__ == "__main__":
    main()
