// Exp 4: Linux system calls integrated with a sugarcane advisory workflow.
// Compile: g++ -std=c++17 -Wall -Wextra -O2 src/os_pipeline.cpp -o build/os_pipeline
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <string>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>
#include <chrono>
#include <filesystem>
using namespace std;
namespace fs = std::filesystem;

bool write_all(int fd, const string &message) {
    size_t n=0;
    while(n<message.size()) {
        ssize_t w=write(fd,message.data()+n,message.size()-n);
        if(w<0 && errno==EINTR) continue;
        if(w<=0) return false;
        n+=static_cast<size_t>(w);
    }
    return true;
}

bool preview_file(const string& path) {
    int fd=open(path.c_str(),O_RDONLY); // OS file call: open
    if(fd<0) { cerr<<"[FILE] Cannot open "<<path<<": "<<strerror(errno)<<"\n";return false; }
    char buffer[200];
    ssize_t bytes=read(fd,buffer,sizeof(buffer)); // OS file call: read
    if(bytes<0) {cerr<<"[FILE] Read error\n";close(fd);return false;}
    close(fd); // OS file call: close
    cout<<"[FILE] Read "<<bytes<<" bytes from "<<path<<" (preview)\n";
    return true;
}

int run_stage(const string &name,const vector<string> &args) {
    cout<<"[PARENT "<<getpid()<<"] Starting "<<name<<" stage..."<<endl;
    pid_t pid=fork(); // OS process call: fork
    if(pid<0) {perror("fork");return 1;}
    if(pid==0) {
        cout<<"[CHILD "<<getpid()<<", PPID "<<getppid()<<"] exec python3 "<<name<<endl;
        vector<char*> argv;
        argv.push_back(const_cast<char*>("python3"));
        argv.push_back(const_cast<char*>("src/advisory.py"));
        for(const auto &arg : args) argv.push_back(const_cast<char*>(arg.c_str()));
        argv.push_back(nullptr);
        execvp("python3",argv.data()); // OS call: execvp
        perror("execvp");_exit(127);
    }
    int status=0;
    if(waitpid(pid,&status,0)<0) {perror("waitpid");return 1;}
    if(!WIFEXITED(status)||WEXITSTATUS(status)!=0){
        cerr<<"[PARENT] Stage "<<name<<" failed (status "<<status<<")\n";
        return 1;
    }
    cout<<"[PARENT] "<<name<<" completed; child PID "<<pid<<"\n";
    return 0;
}

int main(int argc,char* argv[]) {
    if(argc!=3) {cerr<<"Usage: ./build/os_pipeline INPUT.csv OUTPUT_DIR\n";return 2;}
    const string input=argv[1],outdir=argv[2];
    const string predictions=outdir+"/predictions.csv";
    const string metrics=outdir+"/metrics.json";
    const string summary=outdir+"/advisory_report.txt";
    auto start=chrono::steady_clock::now();
    try { fs::create_directories(outdir); }
    catch(const exception &e){cerr<<e.what()<<"\n";return 2;}
    if(!preview_file(input)) return 2;
    if(run_stage("validate",{"validate",input}))return 2;
    if(run_stage("predict",{"predict",input,predictions,metrics}))return 2;
    if(run_stage("report",{"report",predictions,summary}))return 2;
    if(!preview_file(summary)) return 2;
    const auto duration=chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now()-start).count();
    const string status="OS PIPELINE EXECUTION SUCCESS\nParent PID: "+to_string(getpid())+
            "\nProcessed input: "+input+"\nDuration (ms): "+to_string(duration)+"\n";
    const string statusfile=outdir+"/os_execution_summary.txt";
    int fd=open(statusfile.c_str(),O_WRONLY|O_CREAT|O_TRUNC,0640); // OS file call: open
    if(fd<0 || !write_all(fd,status)) {perror("write");if(fd>=0)close(fd);return 2;}
    if(close(fd)<0) {perror("close");return 2;}
    cout<<status; // OS call: write was used to save it
    cout<<"OUTPUTS: "<<outdir<<endl;
    return 0;
}
