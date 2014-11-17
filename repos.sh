#!/bin/bash

git remote add github git@github.com:wiliamsouza/hystrix-py.git
git remote add bitbucket git@bitbucket.org:wiliamsouza/hystrix-py.git
git remote add gitlab git@gitlab.com:wiliamsouza/hystrix-py.git
git remote set-url --push --add origin git@bitbucket.org:wiliamsouza/hystrix-py.git
git remote set-url --push --add origin git@gitlab.com:wiliamsouza/hystrix-py.git
git remote set-url --push --add origin git@github.com:wiliamsouza/hystrix-py.git
