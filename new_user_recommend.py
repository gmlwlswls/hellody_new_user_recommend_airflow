from dotenv import load_dotenv
import os
import boto3
import pandas as pd
import chardet
import io
from pymongo import MongoClient
from bson.objectid import ObjectId

load_dotenv()
url = "mongodb://wang:0131@3.37.201.211:27017"
client = MongoClient(url)

db = client['hellody']
MOVIES = db['MOVIES']

# AWS key
S3_ACCESS_KEY = os.getenv("AWS_S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("AWS_S3_SECRET_KEY")

# S3 클라이언트 생성
s3 = boto3.client("s3", aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)

# S3 버킷과 파일 경로 설정
bucket = 'spotifymodel'
s3_dir = 'watch-data/watchdata.csv'

# S3에서 파일을 읽어와서 pandas 데이터프레임으로 변환
def read_s3_csv_to_dataframe(bucket, s3_dir):
    # S3에서 파일 가져오기
    response = s3.get_object(Bucket=bucket, Key=s3_dir)
    content = response['Body'].read()
    
    # 파일의 인코딩 감지
    result = chardet.detect(content)
    encoding = result['encoding']
    
    # 컬럼명 정의
    # column_names = ["USER_ID", "VOD_ID", "START_DATE"]
    
    # 데이터프레임으로 읽기
    df = pd.read_csv(io.StringIO(content.decode(encoding)))
    
    return df

# 데이터프레임 읽기
df = read_s3_csv_to_dataframe(bucket, s3_dir)

# VOD_ID의 상위 20개를 리스트로 저장
top_20_vod_ids = df['vod_id'].value_counts().head(20).index.tolist()
popular_list = []
for movie_id in top_20_vod_ids:
    vod_list = MOVIES.find_one({'MOVIE_ID':movie_id}, {'_id':0, 'TITLE':1, 'VOD_ID':1, 'POSTER':1})
    popular_list.append(vod_list)
# print(popular_list)

# 결과 출력
# print("상위 20개 VOD_ID 리스트:", top_20_vod_ids)
# 데이터프레임 확인
print(df)

#MongoDB vod_list 업데이트
new_user = db['new_user']
# MongoDB 추천 VOD 리스트 업데이트
new_user.update_one(
    {'_id' : ObjectId('66722754627bdb39ea8a7d17')},
            { 
                "$set": {
                    "new_user": popular_list
          }
      },
    )

print("MongoDB 업데이트 완료")