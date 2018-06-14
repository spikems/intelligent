basepath=$(cd `dirname $0`; cd ..;pwd)
datapath=$basepath/unittest/data
toolpath=$basepath/tool
no=8

sleep 3
echo
echo "brandfind test"
echo
cat $datapath/test.dat | python $toolpath/access.py $no brandfind

sleep 3
echo
echo "intention test"
echo
cat $datapath/test.dat | python $toolpath/access.py $no intention

sleep 3
echo
echo "tongxin test"
echo
cat $datapath/test.dat | python $toolpath/access.py $no tongxin

sleep 3
echo
echo "mzcbase test"
echo
cat $datapath/test.dat | python $toolpath/access.py $no mzcbase

sleep 3
echo
echo "mzczr test"
echo
cat $datapath/test.dat | python $toolpath/access.py $no mzcziran
sleep 3

echo
echo "platform test"
echo
python $toolpath/platform_predict.py $datapath/test.dat.xlsx
