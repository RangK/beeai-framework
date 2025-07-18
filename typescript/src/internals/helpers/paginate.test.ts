/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { paginate, PaginateInput } from "@/internals/helpers/paginate.js";

describe("paginate", () => {
  const mockSetup = [
    {
      size: 1,
      chunkSize: 1,
      items: Array(100).fill(1),
    },
    {
      size: 10,
      chunkSize: 1,
      items: [],
    },
    {
      size: 11,
      chunkSize: 10,
      items: Array(100).fill(1),
    },
    {
      size: 25,
      chunkSize: 1,
      items: Array(20).fill(1),
    },
  ] as const;

  describe("paginate", () => {
    it.each(mockSetup)("Works %#", async ({ size, items, chunkSize }) => {
      const fn: PaginateInput<number, number>["handler"] = vi
        .fn()
        .mockImplementation(async ({ cursor = 0 }) => {
          const chunk = items.slice(cursor, cursor + chunkSize);
          const nextCursor = cursor + chunk.length;
          const done = nextCursor >= items.length;
          return { nextCursor: done ? undefined : nextCursor, data: chunk };
        });

      const results = await paginate({
        size,
        handler: fn,
      });

      const maxItemsToBeRetrieved = Math.min(size, items.length);
      let expectedCalls = Math.ceil(maxItemsToBeRetrieved / chunkSize);
      if (expectedCalls === 0 && size > 0) {
        expectedCalls = 1;
      }
      expect(fn).toBeCalledTimes(expectedCalls);
      expect(results).toHaveLength(maxItemsToBeRetrieved);
    });
  });
});
