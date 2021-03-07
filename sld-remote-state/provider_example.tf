terraform {
  backend "http" {
    address = "http://localhost:8080/terraform_state/4cdd0c76-d78b-11e9-9bea-db9cd8374f3n"
    lock_address = "http://localhost:8080/terraform_lock/4cdd0c76-d78b-11e9-9bea-db9cd8374f3n"
    lock_method = "PUT"
    unlock_address = "http://localhost:8080/terraform_lock/4cdd0c76-d78b-11e9-9bea-db9cd8374f3n"
    unlock_method = "DELETE"
  }
}

provider "aws" {
  region = "${var.region}"
}

