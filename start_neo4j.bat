@echo off
set JAVA_HOME=C:\Program Files\Microsoft\jdk-21.0.9.10-hotspot
set PATH=%JAVA_HOME%\bin;%PATH%
cd /d D:\vsprogram\mapKnowledge\neo4j-community-5.26.1\bin
neo4j.bat console
