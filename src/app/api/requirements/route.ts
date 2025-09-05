import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET() {
  try {
    const requirements = await prisma.requirement.findMany({
      orderBy: { createdAt: 'desc' }
    })

    return NextResponse.json(requirements)
  } catch (error) {
    console.error('Failed to fetch requirements:', error)
    return NextResponse.json(
      { error: 'Failed to fetch requirements' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json()

    const requirement = await prisma.requirement.create({
      data: {
        jobTitle: data.jobTitle,
        client: data.client,
        primeVendor: data.primeVendor,
        status: data.status,
        nextSteps: data.nextSteps,
        vendorInfo: data.vendorInfo,
        consultants: data.consultants,
        interviewId: data.interviewId,
        userId: 'temp-user-id' // Would come from auth
      }
    })

    return NextResponse.json(requirement)
  } catch (error) {
    console.error('Failed to create requirement:', error)
    return NextResponse.json(
      { error: 'Failed to create requirement' },
      { status: 500 }
    )
  }
}