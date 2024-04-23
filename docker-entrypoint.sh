#!/bin/sh

conver_to_array(){
    local TEMP_ARRAY=$1
    local IFS=","
    str=""
    for admin_id in ${TEMP_ARRAY};do
        str="$str    - ${admin_id}\n"
    done
    result=`echo -e "${str}"`
}

if [ ! -e "/V2Board-Telegram-Bot/config.yml" ]; then
    ssh_conn_info=""
    case ${V2BOARD_SSH_ENABLE} in
        false)
            ssh_conn_info=`echo -e "  ssh:\n    enable: ${V2BOARD_SSH_ENABLE}\n"`
        ;;
        true)
            ssh_conn_info=`echo -e "  ssh:\n    enable: ${V2BOARD_SSH_ENABLE}\n    ip: ${V2BOARD_SSH_IP}\n    port: ${V2BOARD_SSH_PORT}\n    user: ${V2BOARD_SSH_USER}\n"`
        ;;
        *)
            echo "Missing environment V2BOARD_SSH_ENABLE."
            exit 1
    esac
    
    ssh_auth_info=""
    if [ "${V2BOARD_SSH_ENABLE}" == "true" ];then
        case ${V2BOARD_SSH_TYPE} in
            passwd)
                ssh_auth_info=`echo -e "    type: ${V2BOARD_SSH_TYPE}\n    pass: ${V2BOARD_SSH_PASS}"`
            ;;
            pkey)
                ssh_auth_info=`echo -e "    type: ${V2BOARD_SSH_TYPE}\n    keyfile: sshkey.pem\n    keypass: ${V2BOARD_SSH_KEYPASS}"`
            cat > sshkey.pem << EOF
${V2BOARD_SSH_KEY}
EOF
            ;;
            *)
                echo "Missing environment V2BOARD_SSH_TYPE."
                exit 2
        esac
    fi
    conver_to_array ${BOT_ADMIN_ID}
    BOT_ADMIN_ID_env=${result}
    cat > /V2Board-Telegram-Bot/config.yml << EOF
bot:
  website: ${BOT_WEBSITE}
  sublink: ${BOT_SUBLINK}
  token: ${BOT_TOKEN}
  admin_id:
${result}
  group_id: ${BOT_GROUP_ID}
  delete_time: ${BOT_DELETE_TIME}
v2board:
  database:
    ip: ${V2BOARD_DB_IP}
    port: ${V2BOARD_DB_PORT}
    user: ${V2BOARD_DB_USER}
    pass: ${V2BOARD_DB_PASS}
    name: ${V2BOARD_DB_NAME}
${ssh_conn_info}
${ssh_auth_info}
EOF
fi
exec "$@"
