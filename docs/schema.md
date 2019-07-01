#Database Schema

This document outlines the database schema used in this tool. This tool only uses one relation, and it takes the following schema:

                                           Table "public.chatanalytics"
     Column     |          Type          | Collation | Nullable |                     Default                      
----------------+------------------------+-----------+----------+--------------------------------------------------
 output_id      | integer                |           | not null | nextval('chatanalytics_output_id_seq'::regclass)
 channelname    | text                   |           | not null |
 date           | date                   |           | not null |
 time           | time without time zone |           | not null |
 nummessages    | integer                |           | not null |
 question       | integer                |           |          |
 disappointment | integer                |           |          |
 funny          | integer                |           |          |
 neutral        | integer                |           |          |
Indexes:
