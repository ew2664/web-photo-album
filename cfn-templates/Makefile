include ../makefile.env

.DEFAULT_GOAL := help

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Deploy
.PHONY: photo-album
photo-album: ## deploy photo-album stack to AWS
	aws cloudformation deploy --template-file photo-album.yaml --stack-name photo-album --capabilities CAPABILITY_NAMED_IAM \
	--parameter-overrides LambdaCodeSourceBucket=$(LAMBDA_CODE_SOURCE_BUCKET) LexBotId=$(LEX_BOT_ID) LexBotAliasId=$(LEX_BOT_ALIAS_ID)

.PHONY: frontend-pipeline
frontend-pipeline: ## deploy frontend pipeline to AWS
	aws cloudformation deploy --template-file frontend-pipeline.yaml --stack-name frontend-pipeline --capabilities CAPABILITY_NAMED_IAM \
	--parameter-overrides CodestarConnId=$(CODESTAR_CONN_ID) GitHubUser=$(GITHUB_USER) GitHubRepo=$(GITHUB_REPO)

.PHONY: lambda-pipeline
lambda-pipeline: ## deploy lambda pipeline to AWS
	aws cloudformation deploy --template-file lambda-pipeline.yaml --stack-name lambda-pipeline --capabilities CAPABILITY_NAMED_IAM \
	--parameter-overrides CodestarConnId=$(CODESTAR_CONN_ID) GitHubUser=$(GITHUB_USER) GitHubRepo=$(GITHUB_REPO) LambdaCodeSourceBucket=$(LAMBDA_CODE_SOURCE_BUCKET)