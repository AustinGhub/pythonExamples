 #include "icsmm.h"
#include "debug.h"
#include "helpers.h"
#include <stdio.h>
#include <stdlib.h>

/*
 * The allocator MUST store the head of its free list in this variable. 
 * Doing so will make it accessible via the extern keyword.
 * This will allow ics_freelist_print to access the value from a different file.
 */
ics_free_header *freelist_head = NULL;
void *currPage;
int pageNumber = 0;
void* epilogue = NULL;
void* prologue = NULL;
/*

 * This is your implementation of malloc. It acquires uninitialized memory from  
 * ics_inc_brk() that is 16-byte aligned, as needed.
 *
 * @param size The number of bytes requested to be allocated.
 *
 * @return If successful, the pointer to a valid region of memory of at least the
 * requested size is returned. Otherwise, NULL is returned and errno is set to 
 * ENOMEM - representing failure to allocate space for the request.
 * 
 * If size is 0, then NULL is returned and errno is set to EINVAL - representing
 * an invalid request.
 */
void *ics_malloc(size_t size) { //get out the block -> split block depending on malloc -> update header and footer -> rest all pointers
    if (size == 0){
        errno = EINVAL;
        return NULL;
    }


    int numNeed = pagesNeeded(size);
    //pageNumber += numNeed;
    if(numNeed>6 || pageNumber >= 6){
        errno = ENOMEM;
        return NULL;
    }

    void *openblock = NULL;
    //determine pages needed
    
    if(pageNumber == 0){
        // curr page has previous start of brk
        currPage = ics_inc_brk(numNeed);//make all the pages with the amount of bytes and the brk ptr still points to the current page
        prologue = currPage;
        epilogue = ics_get_brk()-8;
        int padAmt = (PAGE_SIZE * numNeed)-16;
        currPage = firstPage(currPage,padAmt); // make the first page
        freelist_head = (ics_free_header*)(currPage); // make it the head free list head points to head of block
        freelist_head->next = NULL;
        freelist_head->prev = NULL;
        pageNumber = numNeed;
    }
    else if(pageNumber >= 1 && freelist_head == NULL){
        //EXISTING EPILOGUE BECOMES HEADER OF THE NEW BLOCK
        //make new footer at the end of however many pages were made
        currPage = ics_inc_brk(numNeed)-8;//make all the pages with the amount of bytes and the brk ptr still points to the current page

        if(currPage == (void*)-1){
            errno = ENOMEM;
            return NULL;
        }

        //prologue = currPage;//is actually the header in this case
        epilogue = ics_get_brk()-8;
        int padAmt = (PAGE_SIZE * numNeed);
        currPage = nextPage(currPage,padAmt); // make next Page
        freelist_head = (ics_free_header*)(currPage); // make it the head free list head points to head of block
        freelist_head->next = NULL;
        freelist_head->prev = NULL;
        pageNumber = pageNumber + numNeed;
    }
    else if(pageNumber >= 1 && freelist_head != NULL && size>PAGE_SIZE){
        currPage = ics_inc_brk(numNeed)-8;//make all the pages with the amount of bytes and the brk ptr still points to the current page

        if(currPage == (void*)-1){
            errno = ENOMEM;
            return NULL;
        }
        printf("MICHELLE IS AWESOME\n");
        //prologue = currPage;//is actually the header in this case
        epilogue = ics_get_brk()-8;
        int padAmt = (PAGE_SIZE * numNeed);
        currPage = nextPage(currPage,padAmt); // make next Page
        freelist_head = (ics_free_header*)(currPage); // make it the head free list head points to head of block
        freelist_head->next = NULL;
        freelist_head->prev = NULL;
        pageNumber = pageNumber + numNeed;
    }
    //pageNumber = pageNumber + numNeed;
 

    printf("main size: %ld\n",size);
    openblock = firstFit(size,epilogue); //finds first fit
    if(openblock == NULL){
        printf("openblock is NULL\n");
        return openblock + 8;
    }

    return openblock + 8;
}



/*
 * Marks a dynamically allocated block as no longer in use and coalesces with 
 * adjacent free blocks (as specified by Homework Document). 
 * Adds the block to the appropriate bucket according to the block placement policy.
 *
 * @param ptr Address of dynamically allocated memory returned by the function
 * ics_malloc.
 * 
 * @return 0 upon success, -1 if error and set errno accordingly.
 */
int ics_free(void *ptr) { 
    if(ptr > epilogue || ptr < prologue){
        errno = EINVAL;
        return -1;
    }
    if(ptr != NULL){
        ics_header* checkHead = (ics_header*)(ptr-8);
        ics_footer* checkFoot = (ics_footer*)(ptr+checkHead->block_size -17);//footer

        if(checkHead->hid != HEADER_MAGIC || checkFoot->fid != FOOTER_MAGIC || (checkHead->block_size != checkFoot->block_size)){
            errno = EINVAL;
            return -1;
        }
        //free the block
        checkHead->block_size =checkHead->block_size-1;
        checkFoot->block_size = checkHead->block_size; 
        //free the block

//now check for coalesce
//go from footer of block you are freeing add 8 or 9?? to get to header of next block
//check if allocated bit is 0 (if it is free)
//if 0,coalesce by removing the free block from linked list and merge the block size and update the header  of the free block and and the footer of existing block then insert at head of freelist

        ics_free_header *newHead = (ics_free_header*)(ptr-8);
        ics_header* headerPossibleFree = (ics_header*)(ptr+checkHead->block_size - 8);//gets header
        ics_footer* footerPossibleFree = (ics_footer*)((ptr+checkHead->block_size) + (headerPossibleFree->block_size)-16);
        if(headerPossibleFree->block_size % 2 ==0){

            void* todelete = ptr+ checkHead->block_size -8;
            int coalesce = 0;
            if(pageNumber>= 1 && freelist_head == NULL){
                ics_free_header* block_header = (ics_free_header*) todelete;
                printf("sexy\n");

                checkHead->block_size = (checkHead->block_size)+ headerPossibleFree->block_size;
                footerPossibleFree->block_size = (checkHead->block_size);
                // block_header->next = NULL;
                // block_header->prev = NULL;
                newHead = (ics_free_header*)(ptr-8);
                coalesce = 1;
            }
            else{
                printf("BRO BRO BRO BRO\n");
                deleteNode(todelete);
                checkHead->block_size = (checkHead->block_size)+ headerPossibleFree->block_size;
                footerPossibleFree->block_size = (checkHead->block_size);
                
                newHead = (ics_free_header*)(ptr-8);
                coalesce = 1;
            }

            ics_footer* forFooter = (ics_footer*)(ptr-16);
            ics_header* forHeader = (ics_header*)(ptr-8-forFooter->block_size);
            ics_free_header* deleteForward = (ics_free_header*) ptr - 8 - (forHeader->block_size);
            if(forFooter->fid == FOOTER_MAGIC && forHeader->hid == HEADER_MAGIC && coalesce == 0){
                if(forHeader->block_size % 2 == 0){
                    deleteNode(deleteForward);
                    if(coalesce == 0){
                        forHeader->block_size=(forHeader->block_size)+(headerPossibleFree->block_size);
                        footerPossibleFree->block_size = forHeader->block_size;
                    }
                    else{
                        forHeader->block_size=(forHeader->block_size)+(headerPossibleFree->block_size);
                        checkFoot->block_size=forHeader->block_size;
                    }   
                }
            }


        
        }  

        ics_free_header *temp = freelist_head; // head
        newHead->prev = NULL;
        // newHead->next = temp;
        newHead->next = freelist_head;
        if(freelist_head != NULL){
            // temp->prev = newHead;
            freelist_head->prev = newHead;
            // freelist_head = newHead;
        }
        // printf("added");
        // temp->prev = newHead;
        freelist_head = newHead;
    

        return 0;
    }
    return -1;
}

/********************** EXTRA CREDIT ***************************************/

/*
 * Resizes the dynamically allocated memory, pointed to by ptr, to at least size 
 * bytes. See Homework Document for specific description.
 *
 * @param ptr Address of the previously allocated memory region.
 * @param size The minimum size to resize the allocated memory to.
 * @return If successful, the pointer to the block of allocated memory is
 * returned. Else, NULL is returned and errno is set appropriately.
 *
 * If there is no memory available ics_malloc will set errno to ENOMEM. 
 *
 * If ics_realloc is called with an invalid pointer, set errno to EINVAL. See ics_free
 * for more details.
 *
 * If ics_realloc is called with a valid pointer and a size of 0, the allocated     
 * block is free'd and return NULL.
 */
void *ics_realloc(void *ptr, size_t size) {
    return NULL;
}