WORKSPACE=/vagrant/exercises
# WORKSPACE=/home/netx/hz/assign4/exercises
RESULT_FILE=test_result

function test_lb {
  printf "\n========= lb test ============\n"
  cd $WORKSPACE/load_balance
  make stop > /dev/null 2>&1
  make clean > /dev/null 2>&1
  make lb
}

function test_acl {
  printf "\n========== acl test ==========\n"
  cd $WORKSPACE/acl
  make stop > /dev/null 2>&1
  make clean > /dev/null 2>&1
  make acl
}

if [[ $1 == "acl" ]]; then
  test_acl
elif [[ $1 == "lb" ]]; then
  test_lb
else
  test_acl
  test_lb
fi
