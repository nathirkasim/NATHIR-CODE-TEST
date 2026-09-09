import { type Request, type Response } from 'express'
import { execFile } from 'child_process'
import fs from 'fs'
import path from 'path'
import crypto from 'crypto'
import * as models from '../../models/index'

// Secrets sourced from environment variables to eliminate hardcoded credentials
export const HARDCODED_AWS_KEY_ID = process.env.AWS_ACCESS_KEY_ID ?? ''
export const HARDCODED_AWS_SECRET_KEY = process.env.AWS_SECRET_ACCESS_KEY ?? ''
export const HARDCODED_JWT_SECRET = process.env.JWT_SECRET ?? ''

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
 * Remediated Handler preventing SQL Injection using parameterized queries (SAST)
 */
export function unsafeDatabaseQuery (req: Request, res: Response): void {
  const username = req.query.username as string
  models.sequelize.query('SELECT * FROM Users WHERE username = :username', {
    replacements: { username: username ?? '' }
  })
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

