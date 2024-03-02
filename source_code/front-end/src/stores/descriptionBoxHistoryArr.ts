import { defineStore } from 'pinia'

export const useDescriptionBoxHistoryArrStore = defineStore('descriptionBoxHistoryArr', {
    state: () => ({
        descriptionBoxHistoryArrIndex: 0,
        descriptionBoxHistoryArrLength: 0,
    }),
    actions: {
        increaseIndexByOne(): void {
            this.descriptionBoxHistoryArrIndex += 1
        },
        decreaseIndexByOne(): void {
            this.descriptionBoxHistoryArrIndex -= 1
        },
        increaseLengthByOne(): void {
            this.descriptionBoxHistoryArrLength += 1
        },
        decreaseLengthByOne(): void {
            this.descriptionBoxHistoryArrLength -= 1
        },
        setIndexToZero(): void {
            this.descriptionBoxHistoryArrIndex = 0
        },
        setLengthToZero(): void {
            this.descriptionBoxHistoryArrLength = 0
        },
        increaseIndexAndLengthByOne(): void {
            this.descriptionBoxHistoryArrIndex += 1
            this.descriptionBoxHistoryArrLength += 1
        },
    },
})