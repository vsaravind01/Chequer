from queue import Queue
from typing import Optional
from chequer.ocr_engine.v1.analyse import TextractEngine
from chequer.ocr_engine.models import ChequerTextractQueue, ChequeClearedRecord
from chequer.utils.db_utils import DBSession
from chequer.accounts.models import Account
import json
import asyncio


class TextractQueue:
    """Textract Queue"""

    def __init__(self):
        self.queue = Queue()
        self.textract_engine = TextractEngine()
        self.db_session = DBSession()

    async def add_to_queue(self, image_uri: str, to_account_number: str):
        """Add the image URI to the queue.

        Parameters
        ----------
        - **image_uri**: (str) Image URI
        - **to_account_number**: (str) Account number
        """
        queue_item = ChequerTextractQueue(
            image_uri=image_uri, to_account_number=to_account_number, status="PENDING"
        )
        self.db_session.add_commit(queue_item)
        self.queue.put(queue_item)

    async def process_queue(self):
        """Process the queue.

        Parameters
        ----------
        - **db**: (DBSession) Database session
        """
        db = self.db_session.db
        queue_item = self.queue.get()
        while queue_item is not None:
            queue_item = self.queue.get()
            document = self.textract_engine.analyze_document(queue_item.image_uri)
            response_json = json.dumps(document.response)
            db.add(
                ChequerTextractQueue(
                    image_uri=queue_item.image_uri,
                    to_account_number=queue_item.to_account_number,
                    status="COMPLETED",
                    response=response_json,
                )
            )
            db.commit()

            payee_name = self.textract_engine.get_payee_name(document)
            amount = self.textract_engine.get_amount(document)
            date = self.textract_engine.get_date(document)
            account_number = self.textract_engine.get_account_number(document)
            ifs_code = self.textract_engine.get_ifs_code(document)
            cheque_number = self.textract_engine.get_cheque_number(document)

            from_account = (
                db.query(Account).filter(Account.account_number == account_number).first()
            )

            if from_account is None:
                raise Exception("Account not found")

            to_account = (
                db.query(Account)
                .filter(Account.account_number == queue_item.to_account_number)
                .first()
            )

            if to_account is None:
                raise Exception("Account not found")

            if to_account.name is not payee_name:
                raise Exception("Payee name does not match with the account name")

            db.add(
                ChequeClearedRecord(
                    payer_id=from_account.id,
                    image_url=queue_item.image_uri,
                    cheque_number=cheque_number,
                    ocr_url="",
                    from_account_number=account_number,
                    to_account_number=queue_item.to_account_number,
                    amount=amount,
                    ifs_code=ifs_code,
                    cheque_date=date,
                )
            )
            db.commit()
            self.queue.task_done()

    def get_queue(self):
        """Get the queue."""
        return list(self.queue.queue)

    def get_queue_item(self, queue_id: int):
        """Get the queue item by queue ID.

        Parameters
        ----------
        - **queue_id**: (int) Queue ID
        """
        db = self.db_session.db
        queue_item = (
            db.query(ChequerTextractQueue).filter(ChequerTextractQueue.id == queue_id).first()
        )
        return queue_item


class TextractQueueManager:
    """Background service runner for managing Textract queue."""

    def __init__(self, textract_queue: Optional[TextractQueue] = None):
        self.textract_queue = textract_queue if textract_queue is not None else TextractQueue()

    async def process_queue_forever(self):
        """Continuously process the queue."""
        while True:
            await self.textract_queue.process_queue()
            await asyncio.sleep(1)  # Adjust sleep time as needed

    async def add_to_queue_async(self, image_uri: str, to_account_number: str):
        """Add an item to the queue asynchronously.

        Parameters
        ----------
        - **image_uri**: (str) Image URI
        - **to_account_number**: (str) Account number
        """
        await self.textract_queue.add_to_queue(image_uri, to_account_number)

    def run_forever(self):
        """Run the queue manager forever."""
        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self.process_queue_forever())
            loop.run_forever()
        except KeyboardInterrupt:
            pass
