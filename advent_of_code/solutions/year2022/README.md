# Advent of Code Year 2022

## Background

### Day 17

Absolutely disliked this problem. It's one of those: "I did the first part, should be easy to the second". I then proceed to gallop to my demise.

#### Notes

* The main idea is to find the repeating pattern cycle and simulate what happens before the cycle, during a single cycle, and after the cycle. We can then add the rest as a multiplication of `n - 1` cycles times their individual height contribution.
