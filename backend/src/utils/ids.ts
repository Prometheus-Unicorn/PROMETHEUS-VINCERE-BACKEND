import {randomUUID} from "node:crypto";

export const createJobId = (): string => {
  return `job_${randomUUID()}`;
};

export const createEditSessionId = (): string => {
  return `edit_${randomUUID()}`;
};
