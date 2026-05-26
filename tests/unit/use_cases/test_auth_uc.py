# @pytest.mark.asyncio
# async def test_log_user_success(mock_session,
# mock_users_repo, mock_tokens_repo, session_id_generator, uuid_generator):
#     login_data = LoginData(username=VALID_USERNAME, password=SecretStr("Password123!"))
#     expected_session_id = next(session_id_generator)
#     user_id = next(uuid_generator)
#
#     with (
#         patch("app.application.use_cases.auth.check_user_can_log", new_callable=AsyncMock) as mock_check,
#         patch("app.application.use_cases.auth.generate_session_id") as mock_gen_session,
#         patch("app.application.use_cases.auth.prevent_timing_attack", new_callable=AsyncMock) as mock_prevent,
#     ):
#         mock_check.return_value = user_id
#         mock_gen_session.return_value = expected_session_id
#
#         use_case = LogUser(
#             session=mock_session,
#             users_repo=mock_users_repo,
#             tokens_repo=mock_tokens_repo,
#             login_data=login_data,
#         )
#
#         result = await use_case.execute()
#
#         mock_check.assert_called_once_with(mock_users_repo, login_data)
#         mock_prevent.assert_not_called()
#         mock_gen_session.assert_called_once()
#
#         mock_tokens_repo.add_session.assert_called_once()
#         call_args = mock_tokens_repo.add_session.call_args
#         assert call_args[0][0] == user_id
#         assert call_args[0][1] == expected_session_id
#         assert isinstance(call_args[0][2], datetime)
#
#         assert call_args[0][2].tzinfo == timezone.utc
#
#         mock_session.commit.assert_called_once()
#
#         assert isinstance(result, LoginOutput)
#         assert result.session_id == expected_session_id
#
#         assert result.expires_in > 0
#
#
# @pytest.mark.asyncio
# async def test_logout_user(mock_session, mock_tokens_repo, session_id_generator):
#     session_id = next(session_id_generator)
#
#     use_case = LogoutUser(session=mock_session, tokens_repo=mock_tokens_repo)
#
#     await use_case.execute(session_id=session_id)
#
#     mock_tokens_repo.invalidate_session.assert_called_once_with(session_id)
#     mock_session.commit.assert_called_once()
