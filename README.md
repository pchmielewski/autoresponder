# MySQL Postfix (and not only) autoresponder with minimum effort
This script is designed to quickly set up autoresponder for Postfix with MySQL support.

## How to install
1. Place this script somewhere on your server, for example: /usr/local/sbin/autoresponder.py
2. *# chmod a+x /usr/local/sbin/autoresponder.py*
3. Open autoresponder.sql and find line with 'autoresponder.yourdomain.com':
  * change yourdomain.com to your domain
  * check table name responsible for tranports and change it if needed  (usually it's *postfix_transport* and change is not needed) 
4. Save changes and execute queries from autoresponder.sql, i.e.
```mysql -uroot < autoresponder.sql``` or use import in phpmyadmin
5. Open /etc/postfix/master.cf and add following line:
```autoresponder unix  -       n       n       -       -       pipe flags=F user=vmail argv=/usr/local/sbin/autoresponder.py $sender $size $recipient```
6. Add new autoresponder to table postfix_autoresponder, i.e.
```INSERT INTO `postfix`.`postfix_autoresponder` (`id`, `email`, `from`, `to`, `message`) VALUES (NULL, 'name@yourdomain.com', '2016-07-12 17:00:00', '2016-11-31 23:59:59', 'Out of office');```

Autoresponder will be only active between chosen dates so you can set them in advance and don't need to rememeber about deleting.

## How to configure

You can edit the defaults in the script.


## Requirements

Python 2.7 

(I have not tested this with Python 3)


## Contact

If you have comments or improvements, let me know:

Patryk Chmielewski
patryk.chmielewski@gmail.com
