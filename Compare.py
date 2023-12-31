from robot.api.deco import keyword, library

@library
class Compare():

    @keyword
    def version_compare(self, v1, v2):
        # This will split both the versions by '.'
        self.v1 = v1
        self.v2 = v2
        arr1 = v1.split(".")
        arr2 = v2.split(".")
        n = len(arr1)
        m = len(arr2)

        # converts to integer from string
        arr1 = [int(i) for i in arr1]
        arr2 = [int(i) for i in arr2]

        # compares which list is bigger and fills
        # smaller list with zero (for unequal delimiters)
        if n > m:
            for i in range(m, n):
                arr2.append(0)
        elif m > n:
            for i in range(n, m):
                arr1.append(0)

        # returns 1 if version 1 is bigger and -1 if
        # version 2 is bigger and 0 if equal
        for i in range(len(arr1)):
            if arr1[i]>arr2[i]:
                return 1
            elif arr2[i]>arr1[i]:
                return -1
        return 0

