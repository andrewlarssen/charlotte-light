#!/bin/bash
DIR=`pwd`
rm -f function.zip
cd venv/lib/python3.8/site-packages
zip -r9 ${DIR}/function.zip . -x "bin/*" -x "*/test/*" -x "*/__pycache__/*" -x "*/tests/*" -x "*/doc/*"
cd $DIR
zip -g function.zip lambda_function.py
zip -r function.zip alexa/
ls -lh function.zip

AWS_PROFILE=home aws s3 cp function.zip s3://bucket/lambda.zip --region eu-west-1
VERSION=`AWS_PROFILE=home aws lambda update-function-code --function-name charlotteLight --s3-bucket bucket --s3-key function.zip --region eu-west-1 --publish | jq '.Version|tonumber'`
AWS_PROFILE=home aws lambda delete-alias --function-name live --name live --region eu-west-1
AWS_PROFILE=home aws lambda create-alias --function-name live --name live --function-version $VERSION --region eu-west-1
