while getopts f: flag
do
	case "$flag" in 
		f)
		  FILE=${OPTARG};;
	esac
done

if [ ${#FILE} -eq 0 ]
then
	echo "No File specified"
	exit 1
fi


version=$(strings $FILE | grep "Linux version")
rodata=$(readelf -s $FILE | grep -i "mark_rodata_ro")
canary=$(readelf -s $FILE | grep -i "stack_chk_fail")
fortify=$(readelf -s $FILE | grep "_chk$")
usercopy=$(readelf -s $FILE | grep "usercopy_warn")
freelist=$(readelf -s $FILE | grep "freelist_state_initialize")
kaslr=$(readelf -s $FILE | grep "rotate_xor")
vmap=$(readelf -s $FILE | grep "free_vmap_stack_cache")

if [ ${#version} -ne 0 ]
then
	echo "Linux Kernel version: $version"
else
	echo "No version Found"
	exit -1
fi
if [ ${#canary} -ne 0 ] 
then
	echo "Kernel Protected with Canary: Yes"
else
	echo "Kernel Protected with Canary: No"
fi

if [ ${#fortity} -ne 0 ]
then
	echo "Kernel Protected with Fortify: Yes"
else
	echo "Kernel Protected with Fortify: No"
fi
	
if [ ${#rodata} -ne 0 ]
then
	echo "Kernel Protected with STRICT_RWX: Yes"
else
	echo "Kernel Protected with STRICT_RWX: No"
fi
if [ ${#usercopy} -ne 0 ]
then
	echo "Kernel Protected with USERCOPY: Yes"
else
	echo "Kernel Protected with USERCOPY: No"
fi
if [ ${#freelist} -ne 0 ]
then
	echo "Kernel Protected with FREELIST: Yes"
else
	echo "Kernel Protected with FREELIST: No"
fi
if [ ${#kaslr} -ne 0 ]
then
	echo "Kernel protected with KASLR: Yes"
else
	echo "Kernel protected with KASLR: No"
fi
if [ ${#vmap} -ne 0 ]
then
	echo "Kernel Protected with VMAP: Yes"
else
	echo "Kernel Protected with VMAP: No"
fi

