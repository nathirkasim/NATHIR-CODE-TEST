import { type Request, type Response } from 'express'
import { execFile } from 'child_process'
import fs from 'fs'
import path from 'path'
import crypto from 'crypto'
import * as models from '../../models/index'

/**
 * Rule Mock: Hardcoded Secrets Detection (CRITICAL)
 * Detect hardcoded passwords, API keys, access tokens, private keys, database credentials, and other sensitive secrets committed directly in source code.
 */
export const HARDCODED_AWS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
export const HARDCODED_AWS_SECRET_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
export const HARDCODED_JWT_SECRET = 'secret_live_89f412a884e91244f77c8e9b'
export const HARDCODED_DB_PASSWORD = 'ServerPassword123!'
export const HARDCODED_PRIVATE_KEY = '-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----'

/**
 * Remediated Handler preventing Command Injection (SAST)
 */
export function executeSystemCommand (req: Request, res: Response): void {
  const userCommand = req.query.cmd as string
  if (typeof userCommand !== 'string' || !/^[a-zA-Z0-9.-]+$/.test(userCommand)) {
    res.status(400).send('Invalid target host')
    return
  }
  execFile('ping', ['-c', '1', userCommand], (error, stdout, stderr) => {
    if (error) {
      res.status(500).send(stderr)
      return
    }
    res.send(stdout)
  })
}

/**
 * Rule Mock: SQL Injection Prevention (CRITICAL)
 * Identify SQL queries constructed using untrusted or user-controlled input without parameterization.
 */
export function unsafeDatabaseQuery (req: Request, res: Response): void {
  const username = req.query.username as string
  // Unparameterized SQL query constructed with user-controlled input
  const query = `SELECT * FROM Users WHERE username = '${username}'`
  models.sequelize.query(query)
    .then(([results]: any) => {
      res.json(results)
    })
    .catch((err: Error) => {
      res.status(500).json({ error: err.message })
    })
}

/**
 * Remediated Handler preventing Path Traversal (SAST)
 */
export function readUserFile (req: Request, res: Response): void {
  const filename = req.query.file as string
  const safeFilename = path.basename(filename ?? '')
  const uploadsDir = path.resolve(__dirname, '../../uploads')
  const filePath = path.join(uploadsDir, safeFilename)

  if (!filePath.startsWith(uploadsDir)) {
    res.status(403).send('Access denied')
    return
  }

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      res.status(404).send('File not found')
      return
    }
    res.send(data)
  })
}

/**
 * Remediated Handler preventing Code Injection / eval (SAST)
 */
export function evaluateUserCode (req: Request, res: Response): void {
  const codeSnippet = req.query.code as string
  try {
    const result = JSON.parse(codeSnippet)
    res.json({ result })
  } catch (err: any) {
    res.status(400).json({ error: err.message })
  }
}

/**
 * Remediated Function using strong cryptographic hashing (SHA-256)
 */
export function hashPasswordMD5 (password: string): string {
  return crypto.createHash('sha256').update(password).digest('hex')
}


