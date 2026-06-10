/** Invite code types. */

export type InviteCodeStatus = 'unused' | 'used' | 'disabled'

export interface InviteCode {
  code: string
  status: InviteCodeStatus
  bound_username: string | null
  bound_qq: string | null
  created_at: string | null
}
