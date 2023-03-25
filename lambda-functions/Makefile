include ../makefile.env

.DEFAULT_GOAL := help

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Build
.PHONY: build
build: build-index-photos build-search-photos ## package all Lambda functions

.PHONY: build-index-photos
build-index-photos: index-photos.zip ## package index-photos Lambda function

.PHONY: build-search-photos
build-search-photos: search-photos.zip ## package search-photos Lambda function

.PHONY: rebuild
rebuild: clean build ## repackage all Lambda functions

index-photos.zip: index-photos/lambda_function.py index-photos/requirements.txt
	./package.sh index-photos

search-photos.zip: search-photos/lambda_function.py search-photos/requirements.txt
	./package.sh search-photos

##@ Artifacts
.PHONY: store
upload: upload-index-photos upload-search-photos ## upload all packaged Lambda functions to S3

.PHONY: upload-index-photos
upload-index-photos: index-photos.zip ## upload packaged index-photos Lambda code to S3
	aws s3 cp index-photos.zip s3://$(LAMBDA_CODE_SOURCE_BUCKET)

.PHONY: upload-search-photos
upload-search-photos: search-photos.zip ## upload packaged search-photos Lambda code to S3
	aws s3 cp search-photos.zip s3://$(LAMBDA_CODE_SOURCE_BUCKET)

.PHONY: reupload
reupload: clean upload ## repackage and upload all Lambda functions

##@ Deploy
.PHONY: deploy
deploy: deploy-index-photos deploy-search-photos ## deploy all packaged Lambda functions to AWS

.PHONY: deploy-index-photos
deploy-index-photos: index-photos.zip ## deploy packaged index-photos Lambda code to AWS
	aws lambda update-function-code --no-cli-pager --function-name index-photos --zip-file fileb://index-photos.zip

.PHONY: deploy-search-photos
deploy-search-photos: search-photos.zip ## deploy packaged search-photos Lambda code to AWS
	aws lambda update-function-code --no-cli-pager --function-name search-photos --zip-file fileb://search-photos.zip

.PHONY: redeploy
redeploy: clean deploy ## repackage and deploy all Lambda functions

##@ Cleanup
.PHONY: clean
clean: ## remove all temporary files
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -f *.zip
	rm -rf */package