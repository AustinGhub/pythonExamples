#include "helpers.h"
#include "debug.h"




/* Helper function definitions go here */
void *firstPage(void *brkStart, size_t size){
    void *brkEnd = ics_get_brk(); //the end of the page
 
    *((ics_footer*)brkStart) = (ics_footer){.block_size = 0, .fid = PROLOGUE_MAGIC}; //prologue 
    *((ics_header*)(brkStart+8)) = (ics_header){.block_size = size, .hid = HEADER_MAGIC, .padding_amount = 0}; //header

    *((ics_footer *)(brkEnd - 16)) = (ics_footer){.block_size = size, .fid = FOOTER_MAGIC}; // footer

    *((ics_header *)(brkEnd - 8)) = (ics_header){.block_size = 0, .hid = EPILOGUE_MAGIC};   //epilogue

    *((ics_free_header*)(brkStart+8)) = (ics_free_header){.header = (ics_header){.block_size = size, .hid = HEADER_MAGIC, .padding_amount = 0}, .next = NULL, .prev = NULL};
    return brkStart + 8;
}

void *nextPage(void *brkStart, size_t size){
    void *brkEnd = ics_get_brk(); //the end of the page
 
    // *((ics_header*)(brkStart)) = (ics_header){.block_size = size, .hid = HEADER_MAGIC, .padding_amount = 0}; //header

    // *((ics_footer *)(brkEnd - 16)) = (ics_footer){.block_size = size, .fid = FOOTER_MAGIC}; // footer

    // *((ics_header *)(brkEnd - 8)) = (ics_header){.block_size = 0, .hid = EPILOGUE_MAGIC};   //epilogue

    
    *((ics_header*)(brkStart)) = (ics_header){.block_size = size, .hid = HEADER_MAGIC, .padding_amount = 0}; //header

    *((ics_footer *)(brkEnd - 16)) = (ics_footer){.block_size = size, .fid = FOOTER_MAGIC}; // footer

    *((ics_header *)(brkEnd -8)) = (ics_header){.block_size = 0, .hid = EPILOGUE_MAGIC};   //epilogue

    return brkStart;
}

size_t padding(size_t size){
    int padAmt = 16 - (size%16); //16 - (1%16) = 16-1 = 15
                                    //16 - 4 = 12
    size_t newsize;
    if (padAmt != 16){
        newsize =  size + padAmt; //new size = 1 + 15  so new size is 16
                                    // 12 + 4 = 16
        return newsize;
    }

    return size;
}

int pagesNeeded(size_t size){

    //every page is 4096
    if(size <= (size_t)4096){
        return 1;
    }
    else if((size_t) 4096 < size && size <=(size_t)8192){
        return 2;
    }
    else if((size_t)8192 < size && size <= (size_t)12288){
        return 3;
    }
    else if((size_t)12288 < size  && size <=(size_t) 16384){
        return 4;
    }
    else if((size_t)16384 < size  && size <= (size_t)20480){
        return 5;
    }
    else if((size_t)20480 < size && size<= (size_t)24576){
        return 6;
    }
    else{
        return 0;
    }
}

//header changes when there are more values
int usedPage(){
    return 1;
}


//split so add new footer to the top of the first header block
//add a new header after the footer
//min payload is16 since header and footer are 16
//if the remaining size is less than 32 then don't split
//currHD is the current header
void splitBlock(void* currHD, size_t size,void* epilogue){
    ics_free_header* holdNext = ((ics_free_header*)currHD)->next;
    ics_free_header* holdPrev = ((ics_free_header*)currHD)->prev;
    //already know that we need to split becasue the space is smaller than the block size
    ics_header *prevHead = (ics_header*)currHD; 

    //ics_free_header *currHead = (ics_free_header)currHD;


    size_t paddedAsize = padding(size) + 16; //size of thing to be allocated

    size_t remainingFreeblockSize = prevHead->block_size - paddedAsize; //4048
    // printf("BRO SPLIT SEXY PADDED SIZE %ld\n", remainingFreeblockSize); //4048

    if(remainingFreeblockSize < 32){
        paddedAsize+=remainingFreeblockSize;//add to what you allocated
        remainingFreeblockSize = 0;
        printf("remaining is less %ld\n", remainingFreeblockSize);
        //don't keep the block
    }
  

    ics_header* newHead = (ics_header*)(currHD+paddedAsize);// makes the new header

    if((void*)newHead == (void*)epilogue || remainingFreeblockSize == 0){
        freelist_head = NULL;
    }
    else{ 

        newHead->block_size = remainingFreeblockSize;
        printf("THIS IS THE NEWHEAD BLOCK %d\n", newHead->block_size);
        newHead->hid = HEADER_MAGIC;

        freelist_head = (ics_free_header*)(currHD+paddedAsize);// sets new header
        freelist_head->next = holdNext;
        freelist_head->prev = holdPrev;
        
        // printf("THIS IS THE freefoot BLOCK %d\n", 69);
        // ics_footer *freeFoot = (ics_footer *)((void*)newHead+ newHead->block_size - 8); //broken
        // printf("THIS ISEX");
        // freeFoot->block_size = newHead->block_size; // 
        // freeFoot->fid = FOOTER_MAGIC;

        printf("THIS IS THE freefoot BLOCK %d\n", newHead->block_size);
        ics_footer *freeFoot = (ics_footer *)((void*)newHead+newHead->block_size-8); //broken
        printf("THIS ISEX");
        freeFoot->block_size = newHead->block_size; // 
        freeFoot->fid = FOOTER_MAGIC;
    }
    //newHead->padding_amount = padding(size);
    //header + block size -8

    // ics_footer* newFooter = (ics_footer*)(currHD+paddedAsize-8); //makes new footer under 
    // newFooter->block_size = remainingFreeblockSize;

    //freelist_head->header.padding_amount = padding(size);
    // prevHead->block_size = padding(size) + 16 + 1; //malloc
    prevHead->block_size = paddedAsize + 1; //malloc
    // prevHead->block_size = size + 16 + 1; //malloc
    prevHead->padding_amount = paddedAsize-size-16;

//prevheadblock size is 4096

    
    ics_footer* footptr =(ics_footer *)((void*)prevHead + prevHead->block_size -9);
    footptr->block_size = prevHead->block_size;
    footptr->fid = FOOTER_MAGIC;
    printf("PREVHEAD BLOCK SIZE %d, %d\n", prevHead->block_size, footptr->block_size);

    if((void*)footptr == (void*)epilogue){
        printf("THIS IS THE FOOTPTR EPILOGUE\n");
    }
}

void deleteNode(void* delHead){
    ics_free_header* block_header = (ics_free_header*) delHead;

    // if(block_header->prev == NULL){
    //     return;
    // }
    // Update the next and prev pointers of the neighboring nodes.
    if (block_header->prev != NULL) {
        block_header->prev->next = block_header->next;
    } else {
        freelist_head = block_header->next;
    }
    
    if (block_header->next != NULL) {
        block_header->next->prev = block_header->prev;
    } 
    // else {
    //     freelist_head = block_header->prev;
    // }
    
    // Reset the next and prev pointers of the node to be deleted to NULL.
    block_header->next = NULL;
    block_header->prev = NULL;
    return;
}

void *firstFit(size_t size,void*epilogue){
    //void* block;
    ics_free_header *curr = freelist_head;
    size_t testsize = padding(size) + 16; //check if padding is needed
    // size_t testsize = size + 16; //check if padding is needed

    printf("BLOCK SIZE: %d\n",curr->header.block_size);
    while(curr != NULL){
        if(testsize <= curr->header.block_size){ //found enough space in this block
            //addheader(curr);
            //printf("first fit size: %ld\n",size);
            splitBlock((void*)curr, size,epilogue);
            //printf("FOUND enough space\n");
            return curr;
        }
        curr = curr->next;
    }

    return NULL;
}