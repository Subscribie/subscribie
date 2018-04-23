#!/usr/bin/env python                                                            
import sqlite3                                                                   
import argparse                                                                  
                                                                                 
                                                                                 
def up():                                                                        
    con = sqlite3.connect(args.db)                                               
                                                                                 
    cur = con.cursor()                                                           
    cur.execute('''
	ALTER TABLE user
        ADD COLUMN login_token text
    ''')
    con.commit()                                                                 
                                                                                 
def down():                                                                      
    con = sqlite3.connect(args.db)                                               
    cur = con.cursor()                                                           
    cur.execute('''                                                              
    BEGIN TRANSACTION;
    ALTER TABLE user RENAME TO temp_user;

    CREATE TABLE IF NOT EXISTS user (    
        email text,    
        created_at timestamp,    
        active boolean    
       );

    INSERT INTO user
        SELECT email, created_at, active
    FROM 
    temp_user;
    DROP TABLE temp_user;
    ''')                                                                         
    con.commit() 

parser = argparse.ArgumentParser()                                               
parser.add_argument("-db", "-database", default="../../../../data.db", help="Path to the sqlite database")
group = parser.add_mutually_exclusive_group()                                    
group.add_argument("-up", action="store_true", help="Run the 'up' migration.")   
group.add_argument("-down", action="store_true", help="Run the 'down' migration.")
                                                                                 
args = parser.parse_args()                                                       
                                                                                 
if args.up:                                                                      
    print("Running 'up' migration.")                                             
    up()                                                                         
elif args.down:                                                                  
    print("Running 'down' migration.")                                           
    down() 
