import { NextRequest, NextResponse } from 'next/server'
import { DocumentProcessor } from '@/lib/document-processor'
import { EmailService } from '@/lib/email-service'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const techStacksInput = formData.get('techStacks') as string
    const emailConfigStr = formData.get('emailConfig') as string

    if (!file || !techStacksInput) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Process the document
    const processor = new DocumentProcessor()
    const techStacks = processor.parseTechStacks(techStacksInput)
    
    const fileBuffer = Buffer.from(await file.arrayBuffer())
    const result = await processor.processDocument(fileBuffer, techStacks)

    if (!result.success) {
      return NextResponse.json({
        success: false,
        error: result.error
      })
    }

    // Save to database
    const resume = await prisma.resume.create({
      data: {
        filename: file.name,
        originalUrl: '', // Would be uploaded to storage
        processedUrl: '', // Would be uploaded to storage
        status: 'COMPLETED',
        techStacks: techStacks,
        pointsAdded: result.pointsAdded,
        userId: 'temp-user-id' // Would come from auth
      }
    })

    // Send email if configuration provided
    let emailResult = null
    if (emailConfigStr) {
      try {
        const emailConfig = JSON.parse(emailConfigStr)
        if (emailConfig.recipient && emailConfig.sender && result.buffer) {
          const emailService = new EmailService()
          emailResult = await emailService.sendResumeEmail(
            emailConfig,
            result.buffer,
            file.name
          )

          // Log email attempt
          await prisma.emailLog.create({
            data: {
              resumeId: resume.id,
              recipient: emailConfig.recipient,
              subject: emailConfig.subject,
              status: emailResult.success ? 'SENT' : 'FAILED',
              error: emailResult.error,
              sentAt: emailResult.success ? new Date() : null
            }
          })
        }
      } catch (error) {
        console.error('Email processing error:', error)
      }
    }

    return NextResponse.json({
      success: true,
      pointsAdded: result.pointsAdded,
      techStacks: result.techStacks,
      emailSent: emailResult?.success || false,
      downloadUrl: `/api/download/${resume.id}`
    })

  } catch (error) {
    console.error('Resume processing error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}