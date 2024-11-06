#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
//ideally this file would read the contents of the logs and turn the relevant entries(the ones containing sdaria) into csv files so that we can later things with the data
#define ERROR_LOG_FILE "/var/log/apache2/error.log"     
#define ACCESS_LOG_FILE "/var/log/apache2/access.log"    

// writes parsed error data to CSV
void write_error_csv(const char entries[][4][256], int entry_count) {
    FILE *csvfile = fopen("error_log.csv", "w");
    if (csvfile == NULL) {
        perror("Error opening error CSV file");
        return;
    }

    fprintf(csvfile, "timestamp,error,pid,requestby\n");  // CSV header

    for (int i = 0; i < entry_count; i++) {
        fprintf(csvfile, "%s,%s,%s,%s\n", entries[i][0], entries[i][1], entries[i][2], entries[i][3]);
    }

    fclose(csvfile);
    printf("Error data saved to error_log.csv\n");
}

// writes parsed access data to CSV
void write_access_csv(const char entries[][8][256], int entry_count) {
    FILE *csvfile = fopen("access_log.csv", "w");
    if (csvfile == NULL) {
        perror("Error opening access CSV file");
        return;
    }

    fprintf(csvfile, "ip,timestamp,method,path,status,size,referrer,user_agent\n");  // CSV header

    for (int i = 0; i < entry_count; i++) {
        fprintf(csvfile, "%s,%s,%s,%s,%s,%s,%s,%s\n", 
                entries[i][0], entries[i][1], entries[i][2], entries[i][3], 
                entries[i][4], entries[i][5], entries[i][6], entries[i][7]);
    }

    fclose(csvfile);
    printf("Access data saved to access_log.csv\n");
}

// reads and parses error log file
int error_reader(const char *filename, char entries[][4][256]) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening error log file");
        return 0;
    }

    regex_t regex;
    regmatch_t matches[5];
    int entry_count = 0;

    // filter and parse pattern for entries
    char *pattern = "\\[(.*?)\\] \\[(.*?)\\] \\[pid (.*?)\\] \\[client (.*?)\\]";  
    if (regcomp(&regex, pattern, REG_EXTENDED) != 0) {
        perror("Could not compile regex for error log");
        fclose(file);
        return 0;
    }

    char line[1024];
    while (fgets(line, sizeof(line), file)) {
        if (strstr(line, "sdaria") != NULL) {  // entries containing "sdaria"
            if (regexec(&regex, line, 5, matches, 0) == 0) {
                for (int i = 1; i <= 4; i++) {
                    snprintf(entries[entry_count][i - 1], 256, "%.*s", 
                             (int)(matches[i].rm_eo - matches[i].rm_so), line + matches[i].rm_so);
                }
                entry_count++;
                if (entry_count >= 1000) { //limit for number of entries
                    break;
                }
            }
        }
    }

    regfree(&regex);
    fclose(file);
    return entry_count;
}

// reads and parses access log file
int access_reader(const char *filename, char entries[][8][256]) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening access log file");
        return 0;
    }

    regex_t regex;
    regmatch_t matches[9];
    int entry_count = 0;

    //  pattern for access log
    char *pattern = "^(\\S+) - - \\[(.*?)\\] \"(\\S+) (\\S+) \\S+\" (\\d{3}) (\\d+) \"(.*?)\" \"(.*?)\"";
    if (regcomp(&regex, pattern, REG_EXTENDED) != 0) {
        perror("Could not compile regex for access log");
        fclose(file);
        return 0;
    }

    char line[1024];
    while (fgets(line, sizeof(line), file)) {
        if (regexec(&regex, line, 9, matches, 0) == 0) {
            for (int i = 1; i <= 8; i++) {
                snprintf(entries[entry_count][i - 1], 256, "%.*s", 
                         (int)(matches[i].rm_eo - matches[i].rm_so), line + matches[i].rm_so);
            }
            entry_count++;
            if (entry_count >= 1000) {  
                break;
            }
        }
    }

    regfree(&regex);
    fclose(file);
    return entry_count;
}

int main() {
    char error_entries[1000][4][256];   
    char access_entries[1000][8][256];  


    int error_count = error_reader(ERROR_LOG_FILE, error_entries);
    if (error_count > 0) {
        write_error_csv(error_entries, error_count);
    } else {
        printf("No relevant error log entries found.\n");
    }

    int access_count = access_reader(ACCESS_LOG_FILE, access_entries);
    if (access_count > 0) {
        write_access_csv(access_entries, access_count);
    } else {
        printf("No relevant access log entries found.\n");
    }

    return 0;
}
