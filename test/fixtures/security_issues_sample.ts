import { type Request, type Response } from 'express'
import { exec } from 'child_process'
import fs from 'fs'
import path from 'path'
import crypto from 'crypto'
import * as models from '../../models/index'

// Hardcoded Secrets for Secret Scanner Testing
export const HARDCODED_AWS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
export const HARDCODED_AWS_SECRET_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
export const HARDCODED_JWT_SECRET = 'secret_live_89f412a884e91244f77c8e9b'

/**
 * Vulnerable Handler demonstrating Command Injection (SAST)
 */
export function executeSystemCommand (req: Request, res: Response): void {
  const userCommand = req.query.cmd as string
  // Vulnerable to Command Injection
  exec(`ping -c 1 ${userCommand}`, (error, stdout, stderr) => {
    if (error) {
      res.status(500).send(stderr)
      return
    }
    res.send(stdout)
  })
}

/**
 * Vulnerable Handler demonstrating SQL Injection (SAST)
 */
export function unsafeDatabaseQuery (req: Request, res: Response): void {
  const username = req.query.username as string
  // Vulnerable to SQL Injection via string interpolation
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
 * Vulnerable Handler demonstrating Path Traversal (SAST)
 */
export function readUserFile (req: Request, res: Response): void {
  const filename = req.query.file as string
  // Vulnerable to Path Traversal (Arbitrary File Read)
  const filePath = path.join(__dirname, '../../uploads', filename)
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      res.status(404).send('File not found')
      return
    }
    res.send(data)
  })
}

/**
 * Vulnerable Handler demonstrating Code Injection / eval (SAST)
 */
export function evaluateUserCode (req: Request, res: Response): void {
  const codeSnippet = req.query.code as string
  // Vulnerable to Dynamic Code Execution
  try {
    const result = eval(codeSnippet) // eslint-disable-line no-eval
    res.json({ result })
  } catch (err: any) {
    res.status(400).json({ error: err.message })
  }
}

/**
 * Vulnerable Function demonstrating Weak Hashing (SAST)
 */
export function hashPasswordMD5 (password: string): string {
  // Vulnerable weak cryptographic hash algorithm
  return crypto.createHash('md5').update(password).digest('hex')
}
